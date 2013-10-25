"""
Handle searches for :py:class:`tiddlers <tiddlyweb.model.tiddler.Tiddler>`
if the configured :py:class:`store <tiddlyweb.stores.StorageInterface>`
supports search.
"""

import logging

from httpexceptor import HTTP400

from tiddlyweb.control import readable_tiddlers_by_bag
from tiddlyweb.model.collections import Tiddlers
from tiddlyweb.store import StoreMethodNotImplemented, StoreError
from tiddlyweb.web.sendtiddlers import send_tiddlers


LOGGER = logging.getLogger(__name__)


def get_search_query(environ):
    """
    Inspect :py:mod:`tiddlyweb.query <tiddlyweb.web.query>` in the
    environment to find the search query in a parameter named ``q``.
    """
    try:
        search_query = environ['tiddlyweb.query']['q'][0]
    except (KeyError, IndexError):
        raise HTTP400('query string required')
    return search_query


def get_tiddlers(environ):
    """
    Call search in the :py:class:`store <tiddlyweb.store.Store>`
    to get the generator of :py:class:`tiddlers
    <tiddlyweb.model.tiddler.Tiddler>` matching the query found
    by :py:func:`get_search_query`.
    """
    search_query = get_search_query(environ)
    store = environ['tiddlyweb.store']
    tiddlers = store.search(search_query)
    LOGGER.debug('got search results from store')
    return tiddlers


def get(environ, start_response):
    """
    Handle ``GET`` on the search URI.

    Perform a search against the :py:class:`store <tiddlyweb.store.Store>`.

    What search means and what results are returned is dependent
    on the search implementation (if any) in the :py:class:`chosen store
    <tiddlyweb.stores.StorageInterface>`.
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
    except StoreError as exc:
        raise HTTP400('Error while processing search: %s' % exc)

    return send_tiddlers(environ, start_response, tiddlers=candidate_tiddlers)
