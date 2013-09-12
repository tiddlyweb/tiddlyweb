"""
Special bags are a feature implemented in plugins that allow
non-standard collections of data to be represented as a
:py:class:`bag <tiddlyweb.model.bag.Bag>` of :py:class:`tiddlers
<tiddlyweb.model.tiddler.Tiddler>`. An example is `remotebag`_.

.. _remotebag: https://pypi.python.org/pypi/tiddlywebplugins.remotebag

If ``config['special_bag_detectors']`` is set, it is a list of functions
that take two arguments: a WSGI ``environ`` and a string and return either:

* two functions
* None

The first function yields tiddlers, like
:py:func:`tiddlyweb.store.list_bag_tiddlers`. It's arguments are a
WSGI `environ` and a string.

The second function returns a single :py:class:`tiddler
<tiddlyweb.model.tiddler.Tiddler>`. It's arguments are a WSGI
``environ`` and a tiddler object (with at least ``title`` and ``bag`` set).
"""


class SpecialBagError(Exception):
    """
    A generic exception to be raised by special bag implementations.
    """
    pass


def get_bag_retriever(environ, bag):
    """
    When loading :py:class:`bag <tiddlyweb.model.bag.Bag>` or
    :py:class:`tiddlers <tiddlyweb.model.tiddler.Tiddler>` within it
    from the :py:class:`store <tiddlyweb.store.Store>`, this method is
    used to inspect ``config['special_bag_detectors']`` to determine
    if there is a special handler. If there is, the handler is returned
    and used for retrieval, otherwise ``None`` is returned and the store
    is used as normal.
    """
    try:
        config = environ['tiddlyweb.config']
    except KeyError:
        from tiddlyweb.config import config
    testers = config.get('special_bag_detectors', [])
    for bag_tester in testers:
        retriever = bag_tester(environ, bag)
        if retriever:
            return retriever
    return None
