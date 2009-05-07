"""
Tests on select style filters.
"""

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.filters.select import select_by_attribute, select_relative_attribute

tiddlers = [Tiddler('1'), Tiddler('c'), Tiddler('a'), Tiddler('b')]

tags = ['foo', 'bar', 'foo', 'baz']
dates = ['200905090011', '20090509000000', '2008', '2007']
for i, tiddler in enumerate(tiddlers):
    tiddler.tags.append(tags[i])
    tiddler.modified = dates[i]


def test_simple_select():
    selected_tiddlers = select_by_attribute('tag', 'foo', tiddlers)

    assert ['1','a'] == [tiddler.title for tiddler in selected_tiddlers]

def test_negate_select():
    selected_tiddlers = select_by_attribute('tag', 'foo', tiddlers, negate=True)
    assert ['c','b'] == [tiddler.title for tiddler in selected_tiddlers]

def test_simple_sorted_select():
    selected_tiddlers = select_relative_attribute('title', 'c', tiddlers, lesser=True)
    assert ['1','a','b'] == [tiddler.title for tiddler in selected_tiddlers]

def test_sorted_select():
    selected_tiddlers = select_relative_attribute('modified', '2009', tiddlers, greater=True)
    assert ['1','c'] == [tiddler.title for tiddler in selected_tiddlers]

