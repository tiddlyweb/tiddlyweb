
from tiddlyweb.tiddler import Tiddler
from tiddlyweb.recipe import Recipe
from tiddlyweb.bag import Bag
from tiddlyweb.store import Store, NoTiddlerError, NoBagError
from tiddlyweb.serializer import Serializer, TiddlerFormatError
from tiddlyweb.web.http import HTTP404, HTTP415, HTTP409
from tiddlyweb import control
from tiddlyweb import web

def get_revisions(environ, start_response):
    tiddler = _determine_tiddler(environ)
    return _send_tiddler_revisions(environ, start_response, tiddler)

def get(environ, start_response):
    tiddler = _determine_tiddler(environ)
    return _send_tiddler(environ, start_response, tiddler)

def _send_tiddler_revisions(environ, start_response, tiddler):
    store = environ['tiddlyweb.store']

    tmp_bag = Bag('tmp', tmpbag=True, revbag=True)
    for revision in store.list_tiddler_revisions(tiddler):
        tmp_tiddler = Tiddler(title=tiddler.title, revision=revision, bag=tiddler.bag)
        try:
            store.get(tmp_tiddler)
        except NoTiddlerError, e:
            raise HTTP404, 'tiddler %s at revision % not found, %s' % (tiddler.title, revision, e)
        tmp_bag.add_tiddler(tmp_tiddler)

    serialize_type, mime_type = web.get_serialize_type(environ)
    serializer = Serializer(serialize_type)
    serializer.object = tmp_bag

    start_response("200 OK", [('Content-Type', mime_type),
             ('Set-Cookie', 'chkHttpReadOnly=false')])
    return [serializer.to_string()]

def _send_tiddler(environ, start_response, tiddler):

    store = environ['tiddlyweb.store']

    try:
        store.get(tiddler)
    except NoTiddlerError, e:
        raise HTTP404, '%s not found, %s' % (tiddler.title, e)

    serialize_type, mime_type = web.get_serialize_type(environ)
    serializer = Serializer(serialize_type)
    serializer.object = tiddler

    try:
        content = serializer.to_string()
    except TiddlerFormatError, e:
        raise HTTP415, e

    start_response("200 OK",
            [('Content-Type', mime_type)])

    return [content]

def put(environ, start_response):
    tiddler = _determine_tiddler(environ)
    return _put_tiddler(environ, start_response, tiddler)

def _put_tiddler(environ, start_response, tiddler):
    store = environ['tiddlyweb.store']
    length = environ['CONTENT_LENGTH']

    content_type = environ['tiddlyweb.type']

    if content_type != 'text/plain' and content_type != 'application/json':
        raise HTTP415, '%s not supported yet' % content_type

    content = environ['wsgi.input'].read(int(length))
    serialize_type, mime_type = web.get_serialize_type(environ)
    serializer = Serializer(serialize_type)
    serializer.object = tiddler
    serializer.from_string(content.decode('UTF-8'))

    try:
        store.put(tiddler)
    except NoBagError, e:
        raise HTTP409, "Unable to put tiddler, %s. There is no bag named: %s (%s). Create the bag." % \
                (tiddler.title, tiddler.bag, e)

    start_response("204 No Content",
            [('Location', web.tiddler_url(environ, tiddler))])

    return []

def _determine_tiddler(environ):
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
            bag = control.determine_bag_for_tiddler(recipe, tiddler)
        except NoBagError, e:
            raise HTTP404, '%s not found, %s' % (tiddler.title, e)

        bag_name = bag.name
    except KeyError:
        bag_name = environ['wsgiorg.routing_args'][1]['bag_name']

    tiddler.bag = bag_name
    return tiddler

