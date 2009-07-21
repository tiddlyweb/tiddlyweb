"""
Test the abilities of the limit filter.
This is not about query parsing, but rather
handling once we have the filter.
"""

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.filters.limit import limit

tiddlers = [Tiddler('1'), Tiddler('c'), Tiddler('a'), Tiddler('b')]

def test_simple_limit():
    limited_tiddlers = limit(tiddlers, count=2)

    assert ['1','c'] == [tiddler.title for tiddler in limited_tiddlers]


def test_ranged_limit():
    limited_tiddlers = limit(tiddlers, index=1, count=2)

    assert ['c','a'] == [tiddler.title for tiddler in limited_tiddlers]
