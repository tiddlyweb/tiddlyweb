"""
Hooks that allow plugins to define special bags, such as remotebags.
"""


class SpecialBagError(Exception):
    """
    An exception to be raised in the modules which contain
    special bag detectors and their supporting retrievers.
    """
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
