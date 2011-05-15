"""
Make a query into the store to find some
tiddlers and list them in the interface.
"""

import logging

import urllib

from tiddlyweb.control import readable_tiddlers_by_bag
from tiddlyweb.model.collections import Tiddlers
from tiddlyweb.store import StoreMethodNotImplemented, StoreError
from tiddlyweb.web.sendtiddlers import send_tiddlers
from tiddlyweb.web.http import HTTP400


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
    tiddlers = store.search(search_query)
    logging.debug('got search results from store')
    return tiddlers


def get(environ, start_response):
    """
    Perform a search on the store. What search
    means and what results are returned is dependent
    on the search implementation (if any) in the
    chosen store.
    """
    store = environ['tiddlyweb.store']
    filters = environ['tiddlyweb.filters']
    search_query = get_search_query(environ)
    title = 'Search for %s' % search_query
    title = environ['tiddlyweb.query'].get('title', [title])[0]

    try:
        tiddlers = get_tiddlers(environ)

        usersign = environ['tiddlyweb.usersign']

        if filters:
            candidate_tiddlers = Tiddlers(title=title)
        else:
            candidate_tiddlers = Tiddlers(title=title, store=store)
        candidate_tiddlers.is_search = True

        for tiddler in readable_tiddlers_by_bag(store, tiddlers, usersign):
            candidate_tiddlers.add(tiddler)

    except StoreMethodNotImplemented:
        raise HTTP400('Search system not implemented')
    except StoreError, exc:
        raise HTTP400('Error while processing search: %s' % exc)

    return send_tiddlers(environ, start_response, tiddlers=candidate_tiddlers)
