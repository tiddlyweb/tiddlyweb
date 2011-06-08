"""
Hooks that allow plugins to define special bags, such as remotebags.
"""


class SpecialBagError(Exception):
    pass


def get_bag_retriever(environ, bag):
    """
    Inspect config['special_bag_detectors'] to special
    handlers for bags, like remote uris.
    """
    for bag_tester in environ.get('tiddlyweb.config',
            {}).get('special_bag_detectors', []):
        retriever = bag_tester(environ, bag)
        if retriever:
            return retriever
    return None
