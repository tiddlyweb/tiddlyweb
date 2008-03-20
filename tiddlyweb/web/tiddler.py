
from tiddlyweb.tiddler import Tiddler
from tiddlyweb.store import Store, NoTiddlerError
from tiddlyweb.serializer import Serializer, TiddlerFormatError
from tiddlyweb.web.http import HTTP404, HTTP415
from tiddlyweb import web

serializers = {
        'text/x-tiddlywiki': ['wiki', 'text/html; charset=UTF-8'],
        'text/plain': ['text', 'text/plain; charset=UTF-8'],
        'text/html': ['html', 'text/html; charset=UTF-8'],
        'application/json': ['json', 'application/json; charset=UTF-8'],
        'default': ['text', 'text/plain; charset=UTF-8'],
        }

def _tiddler_from_path(environ):
    bag_name = environ['wsgiorg.routing_args'][1]['bag_name']
    tiddler_name = environ['wsgiorg.routing_args'][1]['tiddler_name']
    tiddler_name = web.handle_extension(environ, tiddler_name)

    tiddler = Tiddler(tiddler_name)
    tiddler.bag = bag_name

    return tiddler

def get(environ, start_response):
    tiddler = _tiddler_from_path(environ)

    store = environ['tiddlyweb.store']

    try:
        store.get(tiddler)
    except NoTiddlerError, e:
        raise HTTP404, '%s not found, %s' % (tiddler.title, e)

    serialize_type, mime_type = web.get_serialize_type(environ, serializers)
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
    tiddler = _tiddler_from_path(environ)
    store = environ['tiddlyweb.store']

    content_type = environ['tiddlyweb.type']

    if content_type != 'text/plain':
        raise HTTP415, '%s not supported yet' % content_type

    content = environ['wsgi.input'].read()
    serializer = Serializer(serializers[content_type][0])
    serializer.object = tiddler
    serializer.from_string(content.decode('UTF-8'))

    store.put(tiddler)

    start_response("204 No Content",
            [('Location', web.tiddler_url(environ, tiddler))])

    return []

