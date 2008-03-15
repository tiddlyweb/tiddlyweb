
import urllib

from tiddlyweb.bag import Bag
from tiddlyweb.store import Store
from tiddlyweb.serializer import Serializer
from tiddlyweb import control

# XXX the store should be in the environ!

serializers = {
        'text/html': ['html', 'text/html'],
        'text/plain': ['text', 'text/plain'],
        }

def list(environ, start_response):
    store = environ['tiddlyweb.store']
    bags = store.list_bags()

    start_response("200 OK",
            [('Content-Type', 'text/plain')])

    return [ '%s\n' % bag.name for bag in bags]

def get_tiddlers(environ, start_response):
    filter_string = urllib.unquote(environ['QUERY_STRING'])

    bag_name = environ['wsgiorg.routing_args'][1]['bag_name']
    bag = Bag(bag_name)

    accept = environ.get('tiddlyweb.accept')
    store = environ['tiddlyweb.store']

    try:
        store.get(bag)
    except NoBagError, e:
        start_response("404 Not Found", [('Content-Type', 'text/plain')])
        output = '%s not found' % bag.name
        return [output]

    tiddlers = control.filter_tiddlers_from_bag(bag, filter_string)
    tmp_bag = Bag('tmp_bag')
    for tiddler in tiddlers:
        tmp_bag.add_tiddler(tiddler)

    try:
        serialization, mime_type = serializers[accept]
        serializer = Serializer(tmp_bag, serialization)
    except KeyError:
        start_response("415 Unsupported", [('Content-Type', 'text/plain')])
        output = '%s type unsupported' % accept
        return [output]

    start_response("200 OK", [('Content-Type', mime_type)])
    return [serializer.to_string()]
