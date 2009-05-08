"""
Test the abilities of the sort filter.
This is not about query parsing, but rather
handling once we have the filter.
"""

import py.test

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.filters.sort import sort_by_attribute, ATTRIBUTE_SORT_KEY

        

ATTRIBUTE_SORT_KEY['count'] = int

tiddlers = [Tiddler('1'), Tiddler('c'), Tiddler('a'), Tiddler('b')]
numbs = [5, 24, 13, 8]
dates = ['200905090011', '20090509000000', '2008', '2007']
for i, tiddler in enumerate(tiddlers):
    tiddler.fields['count'] = '%s' % numbs[i]
    tiddler.modified = dates[i]


def test_simple_sort():
    sorted_tiddlers = sort_by_attribute('title', tiddlers)

    assert ['1','a','b','c'] == [tiddler.title for tiddler in sorted_tiddlers]


def test_reverse_sort():
    sorted_tiddlers = sort_by_attribute('title', tiddlers, reverse=True)

    assert ['c','b','a','1'] == [tiddler.title for tiddler in sorted_tiddlers]


def test_count_sort():
    sorted_tiddlers = sort_by_attribute('count', tiddlers)

    assert ['5', '8', '13', '24'] == [tiddler.fields['count'] for tiddler in sorted_tiddlers]

def test_modified_sort():
    sorted_tiddlers = sort_by_attribute('modified', tiddlers)

    assert ['2007', '2008', '20090509000000', '200905090011'] == [tiddler.modified for tiddler in sorted_tiddlers]


def test_modifier_sort():
    py.test.raises(AttributeError, 'sort_by_attribute("blam", tiddlers, reverse=True)')

