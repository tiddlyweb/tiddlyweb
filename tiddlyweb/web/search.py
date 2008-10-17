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
from tiddlyweb.web.tiddlers import send_tiddlers


def get(environ, start_response):
    try:
        search_query = environ['tiddlyweb.query']['q'][0]
        search_query = urllib.unquote(search_query)
        search_query = unicode(search_query, 'utf-8')
    except (KeyError, IndexError):
        raise HTTP400('query string required')

    filter_string = web.filter_query_string(environ)

    store = environ['tiddlyweb.store']
    try:
        tiddlers = store.search(search_query)
    except StoreMethodNotImplemented:
        raise HTTP400('Search system not implemented')

    usersign = environ['tiddlyweb.usersign']

# naively check permissions on the tiddlers
# this means we go to the store multiple times
# to get the policy for the same bag over and over
# XXX we should improve this once it is working
# It's necessary to get the tiddler off the store
# in case we are doing wiki or atom outputs of the
# search.
    tmp_bag = Bag('tmp_bag', tmpbag=True, searchbag=True)
    for tiddler in tiddlers:
        bag = Bag(tiddler.bag)
        store.get(bag)
        try:
            bag.policy.allows(usersign, 'read')
            tmp_bag.add_tiddler(store.get(tiddler))
        except ForbiddenError:
            pass
        except UserRequiredError:
            pass

    if len(filter_string):
        tiddlers = control.filter_tiddlers_from_bag(tmp_bag, filter_string)
        tmp_bag = Bag('tmp_bag', tmpbag=True)
        for tiddler in tiddlers:
            tmp_bag.add_tiddler(tiddler)

    return send_tiddlers(environ, start_response, tmp_bag)
