
from tiddlyweb.tiddler import Tiddler
from tiddlyweb.store import Store, NoTiddlerError
from tiddlyweb.serializer import Serializer
from tiddlyweb.web.http import HTTP404

def get(environ, start_response):
    bag_name = environ['wsgiorg.routing_args'][1]['bag_name']
    tiddler_name = environ['wsgiorg.routing_args'][1]['tiddler_name']
    tiddler = Tiddler(tiddler_name)
    tiddler.bag = bag_name

    store = environ['tiddlyweb.store']
    serializer = Serializer('text')
    serializer.object = tiddler

    try:
        store.get(tiddler)
    except NoTiddlerError, e:
        raise HTTP404, '%s not found, %s' % (tiddler.title, e)
    
    start_response("200 OK",
            [('Content-Type', 'text/plain')])

    return [serializer.to_string()]

