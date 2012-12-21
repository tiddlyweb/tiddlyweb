"""
Access to Tiddlers via the web. GET and PUT
a Tiddler, GET a list of revisions of a Tiddler.
"""

import logging

from httpexceptor import (HTTP404, HTTP415, HTTP412, HTTP409,
        HTTP400, HTTP304, HTTP302)

from tiddlyweb.model.collections import Tiddlers
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import PermissionsError
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler, current_timestring
from tiddlyweb.store import (NoTiddlerError, NoBagError, NoRecipeError,
        StoreMethodNotImplemented)
from tiddlyweb.serializer import (Serializer, TiddlerFormatError,
        NoSerializationError)
from tiddlyweb.util import pseudo_binary, renderable
from tiddlyweb import control
from tiddlyweb.web.util import (check_bag_constraint, get_route_value,
        handle_extension, content_length_and_type, read_request_body,
        get_serialize_type, tiddler_etag, tiddler_url, encode_name,
        http_date_from_timestamp, check_last_modified)
from tiddlyweb.web.sendtiddlers import send_tiddlers
from tiddlyweb.web.validator import validate_tiddler, InvalidTiddlerError


CACHE_CONTROL_FIELD = '_cache-max-age'
CANONICAL_URI_FIELD = '_canonical_uri'
CANONICAL_URI_PASS_TYPE = 'application/json'


def get(environ, start_response):
    """
    Get a representation of a single tiddler,
    dependent on the chosen serialization and permissions of the
    containing bag.
    """
    tiddler = _determine_tiddler(environ,
            control.determine_bag_from_recipe)
    return _send_tiddler(environ, start_response, tiddler)


def get_revisions(environ, start_response):
    """
    Get the list of revisions for this tiddler.
    """
    tiddler = _determine_tiddler(environ,
            control.determine_bag_from_recipe,
            revisions=True)
    return _send_tiddler_revisions(environ, start_response, tiddler)


def delete(environ, start_response):
    """
    Delete this tiddler from the store. What
    delete means is up to the store.
    """
    tiddler = _determine_tiddler(environ,
            control.determine_bag_from_recipe)
    return _delete_tiddler(environ, start_response, tiddler)


def put(environ, start_response):
    """
    Put a tiddler into the store.
    """
    tiddler = _determine_tiddler(environ,
            control.determine_bag_for_tiddler)
    return _put_tiddler(environ, start_response, tiddler)


def _base_tiddler_object(environ, tiddler_name, revisions):
    """
    Create a tiddler object, without bag or recipe, based on
    URI values.

    ``revisions`` is true when the request is for a revisions
    collection. When true, extension handling is not done on
    the tiddler_name.
    """
    if not revisions:
        try:
            revision = get_route_value(environ, 'revision')
            revision = handle_extension(environ, revision)
        except KeyError:
            tiddler_name = handle_extension(environ, tiddler_name)
            revision = None
    else:
        revision = None

    tiddler = Tiddler(tiddler_name)
    if revision:
        try:
            revision = int(revision)
            tiddler.revision = revision
        except ValueError, exc:
            raise HTTP404('%s not a revision of %s: %s' %
                    (revision, tiddler_name, exc))
    return tiddler


def _delete_tiddler(environ, start_response, tiddler):
    """
    The guts of deleting a tiddler from the store.
    """
    store = environ['tiddlyweb.store']

    try:
        tiddler = store.get(tiddler)
    except NoTiddlerError:
        tiddler.revision = 1
    validate_tiddler_headers(environ, tiddler)

    bag = Bag(tiddler.bag)
    # this will raise 403 if constraint does not pass
    check_bag_constraint(environ, bag, 'delete')

    try:
        store.delete(tiddler)
    except NoTiddlerError, exc:
        raise HTTP404('%s not found, %s' % (tiddler.title, exc))

    start_response("204 No Content", [])
    return []


def _determine_tiddler(environ, bag_finder, revisions=False):
    """
    Determine, using URL info, the target tiddler.
    This can be complicated because of the mechanics
    of recipes and bags.

    Set revisions to True when the current request ends in
    `/revisions` or `/revisions.*`. Doing so ensures that
    processing of extensions does not impact the name of
    the tiddler.
    """
    tiddler_name = get_route_value(environ, 'tiddler_name')
    tiddler = _base_tiddler_object(environ, tiddler_name, revisions)

    # We have to deserialize the tiddler here so that
    # PUTs to recipes are aware of values like tags when
    # doing filter checks.
    if environ['REQUEST_METHOD'] == 'PUT':
        _process_request_body(environ, tiddler)

    try:
        recipe_name = get_route_value(environ, 'recipe_name')
        recipe = Recipe(recipe_name)
        try:
            store = environ['tiddlyweb.store']
            recipe = store.get(recipe)
            tiddler.recipe = recipe_name
        except NoRecipeError, exc:
            raise HTTP404('%s not found via recipe, %s' % (tiddler.title, exc))

        try:
            bag = bag_finder(recipe, tiddler, environ)
        except NoBagError, exc:
            raise HTTP404('%s not found via bag, %s' % (tiddler.title, exc))

        bag_name = bag.name
    except KeyError:
        bag_name = get_route_value(environ, 'bag_name')

    tiddler.bag = bag_name
    return tiddler


def _process_request_body(environ, tiddler):
    """
    Read request body to set tiddler.text.
    """
    length, content_type = content_length_and_type(environ)
    content = read_request_body(environ, length)

    try:
        try:
            serialize_type = get_serialize_type(environ)[0]
            serializer = Serializer(serialize_type, environ)
            # Short circuit de-serialization attempt to avoid
            # decoding content multiple times.
            if hasattr(serializer.serialization, 'as_tiddler'):
                serializer.object = tiddler
                try:
                    serializer.from_string(content.decode('utf-8'))
                except TiddlerFormatError, exc:
                    raise HTTP400('unable to put tiddler: %s' % exc)
            else:
                raise NoSerializationError()
        except NoSerializationError:
            tiddler.type = content_type
            if pseudo_binary(tiddler.type):
                tiddler.text = content.decode('utf-8')
            else:
                tiddler.text = content
    except UnicodeDecodeError, exc:
        raise HTTP400('unable to decode tiddler, utf-8 expected: %s', exc)


def _check_and_validate_tiddler(environ, bag, tiddler):
    """
    If the tiddler does not exist, check we have create
    in the bag. If the tiddler does exist, check we
    have edit. In either case, check ETag to be sure
    that if it is set, that it maches what is currently
    in the store.
    """
    store = environ['tiddlyweb.store']
    try:
        try:
            revision = store.list_tiddler_revisions(tiddler)[0]
        except StoreMethodNotImplemented:
            # If list_tiddler_revisions is not implemented
            # we still need to check if the tiddler exists.
            # If it doesn't NoTiddlerError gets raised and
            # the except block below is run.
            test_tiddler = Tiddler(tiddler.title, tiddler.bag)
            store.get(test_tiddler)
            revision = 1
        tiddler.revision = revision
        # These both next will raise exceptions if
        # the contraints don't match.
        check_bag_constraint(environ, bag, 'write')
        validate_tiddler_headers(environ, tiddler)
    except NoTiddlerError:
        check_bag_constraint(environ, bag, 'create')
        tiddler.revision = 0
        incoming_etag = environ.get('HTTP_IF_MATCH', None)
        if incoming_etag and not (
                incoming_etag == _new_tiddler_etag(tiddler)):
            raise HTTP412('Etag incorrect for new tiddler')


def _put_tiddler(environ, start_response, tiddler):
    """
    The guts of putting a tiddler into the store.

    There's a fair bit of special handling done here
    depending on whether the tiddler already exists or
    not.
    """
    store = environ['tiddlyweb.store']

    try:
        bag = Bag(tiddler.bag)
        _check_and_validate_tiddler(environ, bag, tiddler)

        user = environ['tiddlyweb.usersign']['name']
        if not user == 'GUEST':
            tiddler.modifier = user
        tiddler.modified = current_timestring()

        try:
            check_bag_constraint(environ, bag, 'accept')
        except (PermissionsError), exc:
            _validate_tiddler_content(environ, tiddler)

        store.put(tiddler)
    except NoBagError, exc:
        raise HTTP409("Unable to put tiddler, %s. There is no bag named: "
                "%s (%s). Create the bag." %
                (tiddler.title, tiddler.bag, exc))
    except NoTiddlerError, exc:
        raise HTTP404('Unable to put tiddler, %s. %s' % (tiddler.title, exc))
    except TypeError, exc:
        raise HTTP409('Unable to put badly formed tiddler, %s:%s. %s'
                % (tiddler.bag, tiddler.title, exc))

    etag = ('Etag', tiddler_etag(environ, tiddler))
    response = [('Location', tiddler_url(environ, tiddler))]
    if etag:
        response.append(etag)
    start_response("204 No Content", response)

    return []


def _validate_tiddler_content(environ, tiddler):
    """
    Unless tiddler is valid raise a 409 with the reason why
    things to check are presumably tags and title, but we don't
    want to worry about that here, we want to dispatch elsewhere.
    """
    try:
        validate_tiddler(tiddler, environ)
    except InvalidTiddlerError, exc:
        raise HTTP409('Tiddler content is invalid: %s' % exc)


def validate_tiddler_headers(environ, tiddler):
    """
    Check ETAG and last modified information to
    see if a) the client can use its cached tiddler
    b) we have edit contention when trying to write.
    """
    request_method = environ['REQUEST_METHOD']
    tiddlers_etag = tiddler_etag(environ, tiddler)

    logging.debug('attempting to validate %s with revision %s',
            tiddler.title, tiddler.revision)

    etag = None
    last_modified = None
    if request_method == 'GET':
        incoming_etag = environ.get('HTTP_IF_NONE_MATCH', None)
        if incoming_etag:
            logging.debug('attempting to validate incoming etag(GET):'
                '%s against %s', incoming_etag, tiddlers_etag)
            if incoming_etag == tiddlers_etag:
                raise HTTP304(incoming_etag)
        else:
            last_modified_string = http_date_from_timestamp(
                    tiddler.modified)
            last_modified = ('Last-Modified', last_modified_string)
            check_last_modified(environ, last_modified_string)

    else:
        incoming_etag = environ.get('HTTP_IF_MATCH', None)
        logging.debug('attempting to validate incoming etag(PUT):'
            '%s against %s', incoming_etag, tiddlers_etag)
        if incoming_etag and not _etag_write_match(incoming_etag,
                tiddlers_etag):
            raise HTTP412('Provided ETag does not match. '
                'Server content probably newer.')
    etag = ('Etag', '%s' % tiddlers_etag)
    return last_modified, etag


def _etag_write_match(incoming_etag, server_etag):
    """
    Compare two tiddler etags for a satisfactory match
    for a PUT or DELETE. This means comparing without the
    content type that _may_ be on the end.
    """
    incoming_etag = incoming_etag.split(':', 1)[0].strip('"')
    server_etag = server_etag.split(':', 1)[0].strip('"')
    return (incoming_etag == server_etag)


def _send_tiddler(environ, start_response, tiddler):
    """
    Push a single tiddler out the network in the
    form of the chosen serialization.
    """
    store = environ['tiddlyweb.store']

    bag = Bag(tiddler.bag)
    # this will raise 403 if constraint does not pass
    try:
        check_bag_constraint(environ, bag, 'read')
    except NoBagError, exc:
        raise HTTP404('%s not found, no bag %s, %s' %
                (tiddler.title, tiddler.bag, exc))

    try:
        tiddler = store.get(tiddler)
    except NoTiddlerError, exc:
        raise HTTP404('%s not found, %s' % (tiddler.title, exc))

    # this will raise 304
    # have to do this check after we read from the store because
    # we need the revision, which is sad
    last_modified, etag = validate_tiddler_headers(environ, tiddler)

    # make choices between binary or serialization
    content, mime_type, serialized = _get_tiddler_content(environ, tiddler)

    vary_header = ('Vary', 'Accept')
    cache_header = ('Cache-Control', 'no-cache')
    if CACHE_CONTROL_FIELD in tiddler.fields:
        try:
            cache_header = ('Cache-Control', 'max-age=%s'
                    % int(tiddler.fields[CACHE_CONTROL_FIELD]))
        except ValueError:
            pass  # if the value is not an int use default header

    # Add charset to pseudo_binary tiddler
    if not serialized and pseudo_binary(tiddler.type):
        mime_type = '%s; charset=UTF-8' % mime_type
    content_header = ('Content-Type', str(mime_type))

    response = [cache_header, content_header, vary_header]
    if last_modified:
        response.append(last_modified)
    if etag:
        response.append(etag)
    start_response("200 OK", response)

    if isinstance(content, basestring):
        return [content]
    else:
        return content


def _get_tiddler_content(environ, tiddler):
    """
    Extract the content of the tiddler, either straight up if
    the content is not considered text, or serialized if it is
    """
    config = environ['tiddlyweb.config']
    default_serializer = config['default_serializer']
    default_serialize_type = config['serializers'][default_serializer][0]
    serialize_type, mime_type = get_serialize_type(environ)
    extension = environ.get('tiddlyweb.extension')
    serialized = False

    # If this is a tiddler with a CANONICAL_URI_FIELD redirect
    # there unless we are requesting a json form
    if (CANONICAL_URI_FIELD in tiddler.fields
            and not CANONICAL_URI_PASS_TYPE in mime_type):
        raise HTTP302(tiddler.fields[CANONICAL_URI_FIELD].encode('utf-8'))

    if not renderable(tiddler, environ):
        if (serialize_type == default_serialize_type or
                mime_type.startswith(tiddler.type) or
                extension == 'html'):
            mime_type = tiddler.type
            content = tiddler.text
            return content, mime_type, serialized

    serializer = Serializer(serialize_type, environ)
    serializer.object = tiddler

    try:
        content = serializer.to_string()
        serialized = True
    except (TiddlerFormatError, NoSerializationError), exc:
        raise HTTP415(exc)
    return content, mime_type, serialized


def _send_tiddler_revisions(environ, start_response, tiddler):
    """
    Push the list of tiddler revisions out the network.
    """
    store = environ['tiddlyweb.store']

    title = 'Revisions of Tiddler %s' % tiddler.title
    title = environ['tiddlyweb.query'].get('title', [title])[0]
    container = 'recipes' if tiddler.recipe else 'bags'

    if environ['tiddlyweb.filters']:
        tiddlers = Tiddlers(title=title)
    else:
        tiddlers = Tiddlers(title=title, store=store)

    tiddlers.is_revisions = True
    tiddlers.link = '%s/revisions' % tiddler_url(environ, tiddler,
            container=container, full=False)

    recipe = tiddler.recipe
    try:
        for revision in store.list_tiddler_revisions(tiddler):
            tmp_tiddler = Tiddler(title=tiddler.title, bag=tiddler.bag)
            tmp_tiddler.revision = revision
            if recipe:
                tmp_tiddler.recipe = recipe
            tiddlers.add(tmp_tiddler)
    except NoTiddlerError, exc:
        # If a tiddler is not present in the store.
        raise HTTP404('tiddler %s not found, %s' % (tiddler.title, exc))
    except NoBagError, exc:
        raise HTTP404('tiddler %s not found, bag %s does not exist, %s'
                % (tiddler.title, tiddler.bag, exc))
    except StoreMethodNotImplemented:
        raise HTTP400('no revision support')

    return send_tiddlers(environ, start_response, tiddlers=tiddlers)


def _new_tiddler_etag(tiddler):
    """
    Calculate the ETag of a tiddler that does not
    yet exist. This is a bastardization of ETag handling
    but is useful for doing edit contention handling.
    """
    return str('"%s/%s/%s"' % (encode_name(tiddler.bag),
        encode_name(tiddler.title), '0'))
