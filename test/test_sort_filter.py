"""
Test the abilities of the sort filter.
This is not about query parsing, but rather
handling once we have the filter.
"""

import py.test

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.filters.sort import sort_by_attribute

tiddlers = [Tiddler('1'), Tiddler('c'), Tiddler('a'), Tiddler('b')]

def test_simple_sort():
    sorted_tiddlers = sort_by_attribute('title', tiddlers)

    assert ['1','a','b','c'] == [tiddler.title for tiddler in sorted_tiddlers]


def test_reverse_sort():
    sorted_tiddlers = sort_by_attribute('title', tiddlers, reverse=True)

    assert ['c','b','a','1'] == [tiddler.title for tiddler in sorted_tiddlers]


def test_modifier_sort():
    py.test.raises(AttributeError, 'sort_by_attribute("blam", tiddlers, reverse=True)')

