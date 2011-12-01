"""
Hooks that allow plugins to define special bags, such as remotebags.

If config['special_bag_detectors'] is set, it is a list of functions
that take two arguments: a WSGI environ and a string and return either
* two functions
* None

The first function yields tiddlers, like store.list_bag_tiddlers. It's
arguments are a WSGI environ and a string.

The second function returns a single tiddler. It's arguments are a WSGI
environ and a tiddler object (with at least title and bag set).

See tiddlywebplugins.remotebag for an implementation.
"""


class SpecialBagError(Exception):
    pass


def get_bag_retriever(environ, bag):
    """
    Inspect config['special_bag_detectors'] to special
    handlers for bags, like remote uris.
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
