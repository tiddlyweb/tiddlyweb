"""
Make a query into the store to find some
tiddlers and list them in the interface.
"""

import logging

import urllib

from tiddlyweb.web.http import HTTP400
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import ForbiddenError, UserRequiredError
from tiddlyweb.store import StoreMethodNotImplemented
from tiddlyweb.web.sendtiddlers import send_tiddlers


def get_search_query(environ):
    """
    Inspect tiddlyweb.query in the environment to get
    the search query.
    """
    try:
        search_query = environ['tiddlyweb.query']['q'][0]
        search_query = urllib.unquote(search_query)
    except (KeyError, IndexError):
        raise HTTP400('query string required')
    return search_query


def get_tiddlers(environ):
    """
    Call search in the store with search query to
    get the generator of tiddlers matching the
    query.
    """
    search_query = get_search_query(environ)
    store = environ['tiddlyweb.store']
    try:
        tiddlers = store.search(search_query)
        logging.debug('got search results from store')
    except StoreMethodNotImplemented:
        raise HTTP400('Search system not implemented')
    return tiddlers


def get(environ, start_response):
    """
    Perform a search on the store. What search
    means and what results are returned is dependent
    on the search implementation (if any) in the
    chosen store.
    """
    store = environ['tiddlyweb.store']

    tiddlers = get_tiddlers(environ)

    usersign = environ['tiddlyweb.usersign']

    tmp_bag = Bag('tmp_bag', tmpbag=True, searchbag=True)
    bag_readable = {}

    for tiddler in tiddlers:
        try:
            if bag_readable[tiddler.bag]:
                tmp_bag.add_tiddler(store.get(tiddler))
        except KeyError:
            bag = Bag(tiddler.bag)
            bag.skinny = True
            bag = store.get(bag)
            try:
                bag.policy.allows(usersign, 'read')
                tmp_bag.add_tiddler(store.get(tiddler))
                bag_readable[tiddler.bag] = True
            except(ForbiddenError, UserRequiredError):
                bag_readable[tiddler.bag] = False

    return send_tiddlers(environ, start_response, tmp_bag)
