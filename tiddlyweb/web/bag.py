
import urllib

from tiddlyweb.bag import Bag
from tiddlyweb.store import Store
from tiddlyweb.serializer import Serializer
from tiddlyweb import control
from tiddlyweb.web.http import HTTP415

# XXX the store should be in the environ!

serializers = {
        'text/html': ['html', 'text/html'],
        'text/plain': ['text', 'text/plain'],
        'default': ['html', 'text/html'],
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

    serialize_type, mime_type = _get_serialize_type(environ)
    serializer = Serializer(tmp_bag, serialize_type)

    start_response("200 OK", [('Content-Type', mime_type)])
    return [serializer.to_string()]

def _get_serialize_type(environ):
    # Use the accept headers to look up how we should serialize.
    # If we don't do that, and we had an extension, throw a 415,
    # otherwise, just do a default, this is needed to deal with
    # browsers promiscuiously asking for random stuff like text/xml.
    # It would be better if the info in tiddlyweb.accept was a 
    # list which we traverse until a hit. Will FIXME to do that
    # soonish.
    accept = environ.get('tiddlyweb.accept')
    format = environ.get('wsgiorg.routing_args')[1]['format']
    print "a: %s, f: %s" % (accept, format)
    try:
        serialize_type, mime_type = serializers[accept]
    except KeyError:
        if format:
            raise HTTP415, '%s type unsupported' % format
        serialize_type, mime_type = serializers['default']
    return serialize_type, mime_type
