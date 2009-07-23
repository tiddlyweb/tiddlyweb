"""
Make a query into the store to find some
tiddlers and list them in the interface.
"""

import urllib

from tiddlyweb import control
from tiddlyweb.web.http import HTTP400
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import ForbiddenError, UserRequiredError
from tiddlyweb.store import StoreMethodNotImplemented
from tiddlyweb.web import util as web
from tiddlyweb.web.sendtiddlers import send_tiddlers


def get(environ, start_response):
    """
    Perform a search on the store. What search
    means and what results are returned is dependent
    on the search implementation (if any) in the
    chosen store.
    """
    try:
        search_query = environ['tiddlyweb.query']['q'][0]
        search_query = urllib.unquote(search_query)
        search_query = unicode(search_query, 'utf-8')
    except (KeyError, IndexError):
        raise HTTP400('query string required')

    filters = environ['tiddlyweb.filters']

    store = environ['tiddlyweb.store']
    try:
        tiddlers = store.search(search_query)
    except StoreMethodNotImplemented:
        raise HTTP400('Search system not implemented')

    usersign = environ['tiddlyweb.usersign']

# It's necessary to get the tiddler off the store
# in case we are doing wiki or atom outputs of the
# search.
    tmp_bag = Bag('tmp_bag')
    bag_readable = {}

    def _tiddler_readable(tiddler):
        try:
            if bag_readable[tiddler.bag]:
                return True
        except KeyError:
            bag = Bag(tiddler.bag)
            bag = store.get(bag)
            try:
                bag.policy.allows(usersign, 'read')
                bag_readable[tiddler.bag] = True
                return True
            except (ForbiddenError, UserRequiredError):
                bag_readable[tiddler.bag] = False
                return False

    source_tiddlers = (store.get(tiddler) for tiddler in tiddlers if _tiddler_readable(tiddler))
    tmp_bag.add_tiddler_source(source_tiddlers)

    if len(filters):
        tiddlers = control.filter_tiddlers_from_bag(tmp_bag, filters)
        tmp_bag = Bag('tmp_bag', source=tiddlers)

    return send_tiddlers(environ, start_response, tmp_bag)
