"""
Access to Tiddlers via the web. GET and PUT
a Tiddler, GET a list of revisions of a Tiddler.
"""

import logging
import urllib

import simplejson

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import PermissionsError
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import \
        NoTiddlerError, NoBagError, NoRecipeError, StoreMethodNotImplemented
from tiddlyweb.serializer import Serializer, TiddlerFormatError
from tiddlyweb.util import sha
from tiddlyweb.web.http import \
        HTTP404, HTTP415, HTTP412, HTTP409, HTTP400, HTTP304
from tiddlyweb import control
from tiddlyweb.web import util as web
from tiddlyweb.web.sendtiddlers import send_tiddlers
from tiddlyweb.web.validator import validate_tiddler, InvalidTiddlerError


def get(environ, start_response):
    """
    Get a representation of a single tiddler,
    dependent on the chosen serialization and permissions of the
    containing bag.
    """
    tiddler = _determine_tiddler(environ,
            control.determine_tiddler_bag_from_recipe)
    return _send_tiddler(environ, start_response, tiddler)


def get_revisions(environ, start_response):
    """
    Get the list of revisions for this tiddler.
    """
    tiddler = _determine_tiddler(environ,
            control.determine_tiddler_bag_from_recipe)
    return _send_tiddler_revisions(environ, start_response, tiddler)


def delete(environ, start_response):
    """
    Delete this tiddler from the store. What
    delete means is up to the store.
    """
    tiddler = _determine_tiddler(environ,
            control.determine_tiddler_bag_from_recipe)
    return _delete_tiddler(environ, start_response, tiddler)


def post_revisions(environ, start_response):
    """
    Take a collection of JSON tiddlers, each with a
    text key and value, and process them into the store.
    That collection is known as a TiddlerChronicle.
    """
    tiddler = _determine_tiddler(environ,
            control.determine_tiddler_bag_from_recipe)
    return _post_tiddler_revisions(environ, start_response, tiddler)


def put(environ, start_response):
    """
    Put a tiddler into the store.
    """
    tiddler = _determine_tiddler(environ,
            control.determine_bag_for_tiddler)
    return _put_tiddler(environ, start_response, tiddler)


def _check_bag_constraint(environ, bag, constraint):
    """
    Check to see if the bag allows the current user
    to perform the requested action. Lets NoBagError
    raise.
    """
    try:
        store = environ['tiddlyweb.store']
        usersign = environ['tiddlyweb.usersign']
        bag.skinny = True
        bag = store.get(bag)
        bag.policy.allows(usersign, constraint)
    except (PermissionsError), exc:
        # XXX this throws away traceback info
        msg = 'for bag %s: %s' % (bag.name, exc)
        raise exc.__class__(msg)


def _delete_tiddler(environ, start_response, tiddler):
    """
    The guts of deleting a tiddler from the store.
    """
    store = environ['tiddlyweb.store']

    try:
        tiddler = store.get(tiddler)
    except NoTiddlerError:
        tiddler.revision = 1
    _validate_tiddler_headers(environ, tiddler)

    bag = Bag(tiddler.bag)
    # this will raise 403 if constraint does not pass
    _check_bag_constraint(environ, bag, 'delete')

    try:
        store.delete(tiddler)
    except NoTiddlerError, exc:
        raise HTTP404('%s not found, %s' % (tiddler.title, exc))

    start_response("204 No Content", [])
    return []


def _determine_tiddler(environ, bag_finder):
    """
    Determine, using URL info, the target tiddler.
    This can be complicated because of the mechanics
    of recipes and bags.
    """
    tiddler_name = environ['wsgiorg.routing_args'][1]['tiddler_name']
    tiddler_name = urllib.unquote(tiddler_name)
    tiddler_name = unicode(tiddler_name, 'utf-8')
    revision = environ['wsgiorg.routing_args'][1].get('revision', None)
    if revision:
        revision = web.handle_extension(environ, revision)
    else:
        tiddler_name = web.handle_extension(environ, tiddler_name)

    tiddler = Tiddler(tiddler_name)
    if revision:
        try:
            revision = int(revision)
            tiddler.revision = revision
        except ValueError, exc:
            raise HTTP404('%s not a revision of %s: %s' %
                    (revision, tiddler_name, exc))

    # We have to deserialize the tiddler here so that
    # PUTs to recipes are aware of values like tags when
    # doing filter checks.
    if environ['REQUEST_METHOD'] == 'PUT':
        length, content_type = _length_and_type(environ)

        if content_type != 'text/plain' and content_type != 'application/json':
            tiddler.type = content_type

        content = environ['wsgi.input'].read(int(length))

        if not tiddler.type:
            serialize_type = web.get_serialize_type(environ)[0]
            serializer = Serializer(serialize_type, environ)
            serializer.object = tiddler
            serializer.from_string(content.decode('utf-8'))
        else:
            tiddler.text = content

    recipe_name = environ['wsgiorg.routing_args'][1].get('recipe_name', None)
    if recipe_name:
        recipe_name = urllib.unquote(recipe_name)
        recipe_name = unicode(recipe_name, 'utf-8')
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
    else:
        bag_name = environ['wsgiorg.routing_args'][1]['bag_name']
        bag_name = urllib.unquote(bag_name)
        bag_name = unicode(bag_name, 'utf-8')

    tiddler.bag = bag_name
    return tiddler


def _post_tiddler_revisions(environ, start_response, tiddler):
    """
    We have a list of revisions, put them in a new place.
    """
    content_type = environ['tiddlyweb.type']

    if content_type != 'application/json':
        raise HTTP415('application/json required')

    # we need a matching etag in order to be able to do
    # this operation. This will raise exception if there
    # isn't a valid etag.
    _require_valid_etag_for_write(environ, tiddler)

    bag = Bag(tiddler.bag)
    #  both create and write required for this action
    _check_bag_constraint(environ, bag, 'create')
    _check_bag_constraint(environ, bag, 'write')

    length = environ['CONTENT_LENGTH']
    content = environ['wsgi.input'].read(int(length))

    _store_tiddler_revisions(environ, content, tiddler)

    response = [('Location', web.tiddler_url(environ, tiddler))]
    start_response("204 No Content", response)

    return []


def _store_tiddler_revisions(environ, content, tiddler):
    """
    Given json revisions in content, store them
    as a revision history to tiddler.
    """
    try:
        json_tiddlers = simplejson.loads(content)
    except ValueError, exc:
        raise HTTP409('unable to handle json: %s' % exc)

    store = environ['tiddlyweb.store']
    serializer = Serializer('json', environ)
    serializer.object = tiddler
    for json_tiddler in reversed(json_tiddlers):
        json_string = simplejson.dumps(json_tiddler)
        serializer.from_string(json_string.decode('utf-8'))
        store.put(tiddler)


def _length_and_type(environ):
    """
    To PUT we must have content-length and content-type
    headers. Raise 400 if we cannot get these things.
    """
    try:
        length = environ['CONTENT_LENGTH']
        content_type = environ['tiddlyweb.type']
    except KeyError:
        raise HTTP400(
                'Content-Length and content-type required to put tiddler')
    return length, content_type


def _check_and_validate_tiddler(environ, bag, tiddler):
    """
    If the tiddler does not exist, check we have create
    in the bag, if the tiddler does exist, check we
    have edit. Properly the revision of the tiddler.
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
        _check_bag_constraint(environ, bag, 'write')
        _validate_tiddler_headers(environ, tiddler)
    except NoTiddlerError:
        _check_bag_constraint(environ, bag, 'create')
        tiddler.revision = 0
        incoming_etag = environ.get('HTTP_IF_MATCH', None)
        if incoming_etag and not (
                incoming_etag == _new_tiddler_etag(tiddler)):
            raise HTTP412('Etag incorrect for new tiddler')
    return tiddler.revision


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
        tiddler.revision = _check_and_validate_tiddler(environ, bag, tiddler)

        user = environ['tiddlyweb.usersign']['name']
        if not user == 'GUEST':
            tiddler.modifier = user

        try:
            _check_bag_constraint(environ, bag, 'accept')
        except (PermissionsError), exc:
            _validate_tiddler_content(environ, tiddler)

        store.put(tiddler)
    except NoBagError, exc:
        raise HTTP409("Unable to put tiddler, %s. There is no bag named: " \
                "%s (%s). Create the bag." %
                (tiddler.title, tiddler.bag, exc))
    except NoTiddlerError, exc:
        raise HTTP404('Unable to put tiddler, %s. %s' % (tiddler.title, exc))

    etag = ('Etag', _tiddler_etag(environ, tiddler))
    response = [('Location', web.tiddler_url(environ, tiddler))]
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


def _require_valid_etag_for_write(environ, tiddler):
    """
    Unless there is an etag and it is valid
    we send a 412.
    """
    incoming_etag = environ.get('HTTP_IF_MATCH', None)
    if not incoming_etag:
        raise HTTP412('If Match header required to update tiddlers.')
    tiddler_copy = Tiddler(tiddler.title, tiddler.bag)
    try:
        tiddler_copy = environ['tiddlyweb.store'].get(tiddler_copy)
    except NoTiddlerError:
        tiddler_copy.revision = 0
    return _validate_tiddler_headers(environ, tiddler_copy)


def _validate_tiddler_headers(environ, tiddler):
    """
    Check ETAG and last modified information to
    see if a) the client can use its cached tiddler
    b) we have edit contention when trying to write.
    """
    request_method = environ['REQUEST_METHOD']
    tiddler_etag = _tiddler_etag(environ, tiddler)

    logging.debug('attempting to validate %s with revision %s',
            tiddler.title, tiddler.revision)

    etag = None
    last_modified = None
    if request_method == 'GET':
        incoming_etag = environ.get('HTTP_IF_NONE_MATCH', None)
        if incoming_etag:
            logging.debug('attempting to validate incoming etag(GET):'
                '%s against %s', incoming_etag, tiddler_etag)
            if incoming_etag == tiddler_etag:
                raise HTTP304(incoming_etag)
        else:
            last_modified_string = web.http_date_from_timestamp(
                    tiddler.modified)
            last_modified = ('Last-Modified', last_modified_string)
            incoming_modified = environ.get('HTTP_IF_MODIFIED_SINCE', None)
            if incoming_modified and \
                    (web.datetime_from_http_date(incoming_modified) >=
                            web.datetime_from_http_date(last_modified_string)):
                raise HTTP304('')

    else:
        incoming_etag = environ.get('HTTP_IF_MATCH', None)
        logging.debug('attempting to validate incoming etag(PUT):'
            '%s against %s', incoming_etag, tiddler_etag)
        if incoming_etag and not _etag_write_match(incoming_etag, tiddler_etag):
            raise HTTP412('Provided ETag does not match. '
                'Server content probably newer.')
    etag = ('Etag', '%s' % tiddler_etag)
    return last_modified, etag


def _etag_write_match(incoming_etag, server_etag):
    """
    Compare two tiddler etags for a satisfactory match
    for a PUT or DELETE. This means comparing without the
    content type that _may_ be on the end.
    """
    incoming_etag = incoming_etag.split(';', 1)[0].strip('"')
    server_etag = server_etag.split(';', 1)[0].strip('"')
    return (incoming_etag == server_etag)


def _send_tiddler(environ, start_response, tiddler):
    """
    Push a single tiddler out the network in the
    form of the chosen serialization.
    """
    store = environ['tiddlyweb.store']

    bag = Bag(tiddler.bag)
    # this will raise 403 if constraint does not pass
    _check_bag_constraint(environ, bag, 'read')

    try:
        tiddler = store.get(tiddler)
    except NoTiddlerError, exc:
        raise HTTP404('%s not found, %s' % (tiddler.title, exc))

    # this will raise 304
    # have to do this check after we read from the store because
    # we need the revision, which is sad
    last_modified, etag = _validate_tiddler_headers(environ, tiddler)

    # make choices between binary or serialization
    content, mime_type = _get_tiddler_content(environ, tiddler)

    vary_header = ('Vary', 'Accept')
    cache_header = ('Cache-Control', 'no-cache')
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
    serializers = environ['tiddlyweb.config']['serializers']
    default_serialize_type = serializers['default'][0]
    serialize_type, mime_type = web.get_serialize_type(environ)
    extension = environ.get('tiddlyweb.extension')

    if _not_wikitext(tiddler, environ['tiddlyweb.config']):
        if (serialize_type == default_serialize_type or
                mime_type.startswith(tiddler.type) or
                extension == 'html'):
            mime_type = tiddler.type
            content = tiddler.text
            return content, mime_type

    serializer = Serializer(serialize_type, environ)
    serializer.object = tiddler

    try:
        content = serializer.to_string()
    except TiddlerFormatError, exc:
        raise HTTP415(exc)
    return content, mime_type


def _not_wikitext(tiddler, config):
    """
    Determine if the type of the tiddler indicates
    whether the content is consider wikitext by the
    system. In this context wikitext means something
    that can be rendered.
    """
    return (tiddler.type and # type is set
            tiddler.type != 'None' and # type is not None stringified
            tiddler.type not in # type is not id'd as wikitext by config
            config['wikitext.type_render_map'])


def _send_tiddler_revisions(environ, start_response, tiddler):
    """
    Push the list of tiddler revisions out the network.
    """
    store = environ['tiddlyweb.store']

    tmp_bag = Bag('tmp', tmpbag=True, revbag=True)
    try:
        for revision in store.list_tiddler_revisions(tiddler):
            tmp_tiddler = Tiddler(title=tiddler.title, bag=tiddler.bag)
            tmp_tiddler.revision = revision
            try:
                tmp_tiddler = store.get(tmp_tiddler)
            except NoTiddlerError, exc:
                # If a particular revision is not present in the store.
                raise HTTP404('tiddler %s at revision % not found, %s' %
                        (tiddler.title, revision, exc))
            tmp_bag.add_tiddler(tmp_tiddler)
    except NoTiddlerError, exc:
        # If a tiddler is not present in the store.
        raise HTTP404('tiddler %s not found, %s' % (tiddler.title, exc))
    except StoreMethodNotImplemented:
        raise HTTP400('no revision support')

    return send_tiddlers(environ, start_response, tmp_bag)


def _new_tiddler_etag(tiddler):
    """
    Calculate the ETag of a tiddler that does not
    yet exist. This is a bastardization of ETag handling
    but is useful for doing edit contention handling.
    """
    return str('"%s/%s/%s"' % (web.encode_name(tiddler.bag),
        web.encode_name(tiddler.title), '0'))


def _tiddler_etag(environ, tiddler):
    """
    Calculate the ETAG of a tiddler, based on
    bag name, tiddler title and revision.
    """
    try:
        mime_type = web.get_serialize_type(environ)[1]
        mime_type = mime_type.split(';', 1)[0].strip()
    except TypeError:
        mime_type = ''
    username = environ.get('tiddlyweb.usersign', {}).get('name', '')
    hash = sha('%s:%s' % (username, mime_type)).hexdigest()
    return str('"%s/%s/%s;%s"' % (web.encode_name(tiddler.bag),
        web.encode_name(tiddler.title), tiddler.revision, hash))
