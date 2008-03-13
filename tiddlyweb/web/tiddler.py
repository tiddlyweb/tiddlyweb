
from tiddlyweb.tiddler import Tiddler
from tiddlyweb.store import Store, NoTiddlerError
from tiddlyweb.serializer import Serializer

def get(environ, start_response):
    bag_name = environ['wsgiorg.routing_args'][1]['bag_name']
    tiddler_name = environ['wsgiorg.routing_args'][1]['tiddler_name']
    tiddler = Tiddler(tiddler_name)
    tiddler.bag = bag_name

    store = Store('text')
    serializer = Serializer(tiddler, 'text')

    try:
        store.get(tiddler)
    except NoTiddlerError, e:
        start_response("404 Not Found", [('Content-Type', 'text/plain')])
        output = '%s not found' % tiddler.title
        return [output]
    
    start_response("200 OK",
            [('Content-Type', 'text/plain')])

    return [serializer.to_string()]

