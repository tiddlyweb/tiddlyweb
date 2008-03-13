
import urllib

from tiddlyweb.bag import Bag
from tiddlyweb.store import Store
from tiddlyweb import control

# XXX the store should be in the environ!

def get_tiddlers(environ, start_response):
    filter_string = urllib.unquote(environ['QUERY_STRING'])

    bag_name = environ['wsgiorg.routing_args'][1]['bag_name']
    bag = Bag(bag_name)

    store = Store('text')

    try:
        store.get(bag)
    except NoBagError, e:
        start_response("404 Not Found", [('Content-Type', 'text/plain')])
        output = '%s not found' % recipe.name
        return [output]

    start_response("200 OK",
            [('Content-Type', 'text/plain')])

    return [ '%s\n' % tiddler.title for tiddler in control.filter_tiddlers_from_bag(bag, filter_string)]
