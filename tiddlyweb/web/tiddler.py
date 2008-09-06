"""
Access to Tiddlers via the web. GET and PUT
a Tiddler, GET a list of revisions of a Tiddler.
"""

import urllib

from tiddlyweb.tiddler import Tiddler
from tiddlyweb.recipe import Recipe
from tiddlyweb.bag import Bag
from tiddlyweb.store import NoTiddlerError, NoBagError, StoreMethodNotImplemented
from tiddlyweb.serializer import Serializer, TiddlerFormatError
from tiddlyweb.web.http import HTTP404, HTTP415, HTTP412, HTTP409, HTTP400, HTTP304
from tiddlyweb import control
from tiddlyweb.web import util as web
from tiddlyweb.web.tiddlers import send_tiddlers

def get(environ, start_response):
    tiddler = _determine_tiddler(environ, control.determine_tiddler_bag_from_recipe)
    return _send_tiddler(environ, start_response, tiddler)

def get_revisions(environ, start_response):
    tiddler = _determine_tiddler(environ, control.determine_tiddler_bag_from_recipe)
    return _send_tiddler_revisions(environ, start_response, tiddler)

def delete(environ, start_response):
    tiddler = _determine_tiddler(environ, control.determine_tiddler_bag_from_recipe)
    return _delete_tiddler(environ, start_response, tiddler)

def put(environ, start_response):
    tiddler = _determine_tiddler(environ, control.determine_bag_for_tiddler)
    return _put_tiddler(environ, start_response, tiddler)

def _check_bag_constraint(environ, bag, constraint):
    store = environ['tiddlyweb.store']
    usersign = environ['tiddlyweb.usersign']
    try:
        store.get(bag)
        bag.policy.allows(usersign, constraint)
    except NoBagError, e:
        raise HTTP404, 'bag %s not found, %s' % (bag.name, e)

def _delete_tiddler(environ, start_response, tiddler):
    store = environ['tiddlyweb.store']

    bag = Bag(tiddler.bag)
    # this will raise 403 if constraint does not pass
    _check_bag_constraint(environ, bag, 'delete')

    try:
        store.delete(tiddler)
    except NoTiddlerError, e:
        raise HTTP404, '%s not found, %s' % (tiddler.title, e)

    start_response("204 No Content", [])
    return []

def _determine_tiddler(environ, bag_finder):
    tiddler_name = environ['wsgiorg.routing_args'][1]['tiddler_name']
    tiddler_name = urllib.unquote(tiddler_name)
    tiddler_name = unicode(tiddler_name, 'utf-8')
    revision = environ['wsgiorg.routing_args'][1].get('revision', None)
    if revision:
        revision = web.handle_extension(environ, revision)
    else:
        tiddler_name = web.handle_extension(environ, tiddler_name)

    if revision:
        try:
            revision = int(revision)
        except ValueError, e:
            raise HTTP404, '%s not a revision of %s: %s' % (revision, tiddler_name, e)

    tiddler = Tiddler(tiddler_name)
    tiddler.revision = revision

    recipe_name = environ['wsgiorg.routing_args'][1].get('recipe_name', None)
    if recipe_name:
        recipe_name = urllib.unquote(recipe_name)
        recipe_name = unicode(recipe_name, 'utf-8')
        recipe = Recipe(recipe_name)
        store = environ['tiddlyweb.store']
        store.get(recipe)
        tiddler.recipe = recipe_name

        try:
            bag = bag_finder(recipe, tiddler)
        except NoBagError, e:
            raise HTTP404, '%s not found, %s' % (tiddler.title, e)

        bag_name = bag.name
    else:
        bag_name = environ['wsgiorg.routing_args'][1]['bag_name']
        bag_name = urllib.unquote(bag_name)
        bag_name = unicode(bag_name, 'utf-8')

    tiddler.bag = bag_name
    return tiddler

def _put_tiddler(environ, start_response, tiddler):
    store = environ['tiddlyweb.store']
    length = environ['CONTENT_LENGTH']

    content_type = environ['tiddlyweb.type']

    if content_type != 'text/plain' and content_type != 'application/json':
        raise HTTP415, '%s not supported ' % content_type

    last_modified = None
    etag = None
    try:
        bag = Bag(tiddler.bag)
        try:
            try:
                revision = store.list_tiddler_revisions(tiddler)[0]
            except StoreMethodNotImplemented:
                revision = 1
            tiddler.revision = revision
            _check_bag_constraint(environ, bag, 'write')
            last_modified, etag = _validate_tiddler(environ, tiddler)
        except NoTiddlerError:
            _check_bag_constraint(environ, bag, 'create')

        content = environ['wsgi.input'].read(int(length))
        serialize_type, mime_type = web.get_serialize_type(environ)
        serializer = Serializer(serialize_type, environ)
        serializer.object = tiddler
        serializer.from_string(content.decode('UTF-8'))

        store.put(tiddler)
    except NoBagError, e:
        raise HTTP409, "Unable to put tiddler, %s. There is no bag named: %s (%s). Create the bag." % \
                (tiddler.title, tiddler.bag, e)

    etag = ('Etag', _tiddler_etag(tiddler))
    response = [('Location', web.tiddler_url(environ, tiddler))]
    if etag:
        response.append(etag)
    start_response("204 No Content", response)

    return []

def _validate_tiddler(environ, tiddler):
    request_method = environ['REQUEST_METHOD']
    tiddler_etag = _tiddler_etag(tiddler)

    etag = None
    last_modified = None
    if request_method == 'GET':
        incoming_etag = environ.get('HTTP_IF_NONE_MATCH', None)
        if incoming_etag == tiddler_etag:
            raise HTTP304, incoming_etag
        last_modified_string = web.http_date_from_timestamp(tiddler.modified)
        last_modified = ('Last-Modified', last_modified_string)
        incoming_modified = environ.get('HTTP_IF_MODIFIED_SINCE', None)
        if incoming_modified and \
                (web.datetime_from_http_date(incoming_modified) >= web.datetime_from_http_date(last_modified_string)):
            raise HTTP304, ''

    elif request_method == 'PUT':
        incoming_etag = environ.get('HTTP_IF_MATCH', None)
        if incoming_etag and incoming_etag != tiddler_etag:
            raise HTTP412, 'Etag no match'
    etag = ('Etag', tiddler_etag)
    return last_modified, etag

def _send_tiddler(environ, start_response, tiddler):
    store = environ['tiddlyweb.store']

    bag = Bag(tiddler.bag)
    # this will raise 403 if constraint does not pass
    _check_bag_constraint(environ, bag, 'read')

    try:
        store.get(tiddler)
    except NoTiddlerError, e:
        raise HTTP404, '%s not found, %s' % (tiddler.title, e)

    # this will raise 304
    # have to do this check after we read from the store because
    # we need the revision, which is sad
    last_modified, etag = _validate_tiddler(environ, tiddler)

    serialize_type, mime_type = web.get_serialize_type(environ)
    serializer = Serializer(serialize_type, environ)
    serializer.object = tiddler
    
    try:
        content = serializer.to_string()
    except TiddlerFormatError, e:
        raise HTTP415, e

    cache_header = ('Cache-Control', 'no-cache')
    content_header = ('Content-Type', mime_type)
    response = [cache_header, content_header]
    if last_modified:
        response.append(last_modified)
    if etag:
        response.append(etag)
    start_response("200 OK", response)

    return [content]

def _send_tiddler_revisions(environ, start_response, tiddler):
    store = environ['tiddlyweb.store']

    tmp_bag = Bag('tmp', tmpbag=True, revbag=True)
    try:
        for revision in store.list_tiddler_revisions(tiddler):
            tmp_tiddler = Tiddler(title=tiddler.title, bag=tiddler.bag)
            tmp_tiddler.revision = revision
            try:
                store.get(tmp_tiddler)
            except NoTiddlerError, e:
                # If a particular revision is not present in the store.
                raise HTTP404, 'tiddler %s at revision % not found, %s' % (tiddler.title, revision, e)
            tmp_bag.add_tiddler(tmp_tiddler)
    except NoTiddlerError, e:
        # If a tiddler is not present in the store.
        raise HTTP404, 'tiddler %s not found, %s' % (tiddler.title, e)
    except StoreMethodNotImplemented:
        raise HTTP400, 'no revision support'

    return send_tiddlers(environ, start_response, tmp_bag)

def _tiddler_etag(tiddler):
    return str('%s/%s/%s' % (urllib.quote(tiddler.bag.encode('utf-8')),
        urllib.quote(tiddler.title.encode('utf-8')), tiddler.revision))

