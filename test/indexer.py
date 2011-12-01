"""
A stub module providing an index_query method to test
the recipe indexer functionality.
"""

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.filters import FilterIndexRefused


def index_query(environ, **kwords):
    store = environ['tiddlyweb.store']
    bag_name, tiddler_title = kwords['id'].split(':', 1)
    if bag_name == 'fwoop':
        if tiddler_title == 'swell':
            yield store.get(Tiddler('swell', 'fwoop'))
    raise FilterIndexRefused('bad stuff')
