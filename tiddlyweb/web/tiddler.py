"""
Access to Tiddlers via the web. GET and PUT
a Tiddler, GET a list of revisions of a Tiddler.
"""
from tiddlyweb.tiddler import Tiddler
from tiddlyweb.recipe import Recipe
from tiddlyweb.bag import Bag
from tiddlyweb.store import Store, NoTiddlerError, NoBagError
from tiddlyweb.serializer import Serializer, TiddlerFormatError
from tiddlyweb.web.http import HTTP404, HTTP415, HTTP412, HTTP409, HTTP403, HTTP304
from tiddlyweb import control
from tiddlyweb import web

def get(environ, start_response):
    tiddler = _determine_tiddler(environ, control.determine_tiddler_bag_from_recipe)
    return _send_tiddler(environ, start_response, tiddler)

def get_revisions(environ, start_response):
    tiddler = _determine_tiddler(environ, control.determine_tiddler_bag_from_recipe)
    return _send_tiddler_revisions(environ, start_response, tiddler)

def put(environ, start_response):
    tiddler = _determine_tiddler(environ, control.determine_bag_for_tiddler)
    return _put_tiddler(environ, start_response, tiddler)

def _check_bag_constraint(environ, bag, constraint):
    store = environ['tiddlyweb.store']
    usersign = environ['tiddlyweb.usersign']
    try:
        store.get(bag)
        if not bag.policy.allows(usersign, constraint):
            raise HTTP403, '%s may not %s on %s' % (usersign, constraint, bag.name)
    except NoBagError, e:
        raise HTTP404, 'bag %s not found, %s' % (bag.name, e)

def _determine_tiddler(environ, bag_finder):
    tiddler_name = environ['wsgiorg.routing_args'][1]['tiddler_name']
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

    try:
        recipe_name = environ['wsgiorg.routing_args'][1]['recipe_name']
        recipe = Recipe(recipe_name)
        store = environ['tiddlyweb.store']
        store.get(recipe)

        try:
            bag = bag_finder(recipe, tiddler)
        except NoBagError, e:
            raise HTTP404, '%s not found, %s' % (tiddler.title, e)

        bag_name = bag.name
    except KeyError:
        bag_name = environ['wsgiorg.routing_args'][1]['bag_name']

    tiddler.bag = bag_name
    return tiddler

def _put_tiddler(environ, start_response, tiddler):
    store = environ['tiddlyweb.store']
    length = environ['CONTENT_LENGTH']

    content_type = environ['tiddlyweb.type']

    if content_type != 'text/plain' and content_type != 'application/json':
        raise HTTP415, '%s not supported' % content_type

    try:
        bag = Bag(tiddler.bag)
        try:
            revision = store.list_tiddler_revisions(tiddler)[0]
            tiddler.revision = revision
            _check_bag_constraint(environ, bag, 'write')
            _check_etag(environ, tiddler)
        except NoTiddlerError:
            _check_bag_constraint(environ, bag, 'create')

        content = environ['wsgi.input'].read(int(length))
        serialize_type, mime_type = web.get_serialize_type(environ)
        serializer = Serializer(serialize_type)
        serializer.object = tiddler
        serializer.from_string(content.decode('UTF-8'))

        store.put(tiddler)
    except NoBagError, e:
        raise HTTP409, "Unable to put tiddler, %s. There is no bag named: %s (%s). Create the bag." % \
                (tiddler.title, tiddler.bag, e)

    etag = _tiddler_etag(tiddler)

    start_response("204 No Content",
            [('Location', web.tiddler_url(environ, tiddler)),
                ('Etag', etag)])

    return []

def _check_etag(environ, tiddler):
    request_method = environ['REQUEST_METHOD']
    tiddler_etag = _tiddler_etag(tiddler)

    if request_method == 'GET':
        incoming_etag = environ.get('HTTP_IF_NONE_MATCH', None)
        if incoming_etag == tiddler_etag:
            raise HTTP304, incoming_etag
    elif request_method == 'PUT':
        incoming_etag = environ.get('HTTP_IF_MATCH', None)
        if incoming_etag and incoming_etag != tiddler_etag:
            raise HTTP412, 'Etag no match'
    else:
        return

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
    _check_etag(environ, tiddler)

    serialize_type, mime_type = web.get_serialize_type(environ)
    serializer = Serializer(serialize_type)
    serializer.object = tiddler

    try:
        content = serializer.to_string()
    except TiddlerFormatError, e:
        raise HTTP415, e

    etag = _tiddler_etag(tiddler)

    start_response("200 OK",
            [('Last-Modified', web.http_date_from_timestamp(tiddler.modified)),
                ('Content-Type', mime_type),
                ('Etag', etag)])

    return [content]

def _send_tiddler_revisions(environ, start_response, tiddler):
    store = environ['tiddlyweb.store']

    tmp_bag = Bag('tmp', tmpbag=True, revbag=True)
    try:
        for revision in store.list_tiddler_revisions(tiddler):
            tmp_tiddler = Tiddler(title=tiddler.title, revision=revision, bag=tiddler.bag)
            try:
                store.get(tmp_tiddler)
            except NoTiddlerError, e:
                # If a particular revision is not present in the store.
                raise HTTP404, 'tiddler %s at revision % not found, %s' % (tiddler.title, revision, e)
            tmp_bag.add_tiddler(tmp_tiddler)
    except NoTiddlerError, e:
        # If a tiddler is not present in the store.
        raise HTTP404, 'tiddler %s not found, %s' % (tiddler.title, e)

    serialize_type, mime_type = web.get_serialize_type(environ)
    serializer = Serializer(serialize_type)
    serializer.object = tmp_bag

    start_response("200 OK", [('Content-Type', mime_type),
             ('Set-Cookie', 'chkHttpReadOnly=false')])
    return [serializer.to_string()]

def _tiddler_etag(tiddler):
    return '%s/%s/%s' % (tiddler.bag, tiddler.title, tiddler.revision)

