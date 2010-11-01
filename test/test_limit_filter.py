"""
Test the abilities of the limit filter.
This is not about query parsing, but rather
handling once we have the filter.
"""

import py.test

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.filters.limit import limit
from tiddlyweb.filters import parse_for_filters, recursive_filter, FilterError

tiddlers = [Tiddler('1'), Tiddler('c'), Tiddler('a'), Tiddler('b')]

def test_simple_limit():
    limited_tiddlers = limit(tiddlers, count=2)

    assert ['1','c'] == [tiddler.title for tiddler in limited_tiddlers]


def test_ranged_limit():
    limited_tiddlers = limit(tiddlers, index=1, count=2)

    assert ['c','a'] == [tiddler.title for tiddler in limited_tiddlers]

def test_negative_limit():
    py.test.raises(ValueError, 'limit(tiddlers, index=-1, count=2)')

def test_exception():
    filter, _ = parse_for_filters('limit=-1,2')
    py.test.raises(FilterError, 'recursive_filter(filter, tiddlers)')
