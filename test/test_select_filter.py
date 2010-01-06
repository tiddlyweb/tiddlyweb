"""
Tests on select style filters.
"""

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.filters.select import select_by_attribute, select_relative_attribute, ATTRIBUTE_SELECTOR

tiddlers = [Tiddler('1'), Tiddler('c'), Tiddler('a'), Tiddler('b')]

tags = ['foo', 'bar', 'foo', 'baz']
dates = ['200905090011', '20090509000000', '2008', '2007']
for i, tiddler in enumerate(tiddlers):
    tiddler.tags.append(tags[i])
    tiddler.modified = dates[i]
    tiddler.fields['index'] = str(i)

def has_year(tiddler, attribute, value):
    return tiddler.modified.startswith(value)

ATTRIBUTE_SELECTOR['year'] = has_year


def test_simple_select():
    selected_tiddlers = select_by_attribute('tag', 'foo', tiddlers)

    assert ['1','a'] == [tiddler.title for tiddler in selected_tiddlers]

def test_negate_select():
    selected_tiddlers = select_by_attribute('tag', 'foo', tiddlers, negate=True)
    assert ['c','b'] == [tiddler.title for tiddler in selected_tiddlers]

def test_simple_sorted_select():
    selected_tiddlers = select_relative_attribute('title', 'c', tiddlers, lesser=True)
    assert ['1','a','b'] == [tiddler.title for tiddler in selected_tiddlers]

def test_relative_missing_args():
    """If we forget to set lesser or greater, then we want it all."""
    selected_tiddlers = select_relative_attribute('title', 'c', tiddlers)
    assert ['1','c','a','b'] == [tiddler.title for tiddler in selected_tiddlers]

def test_sorted_select():
    selected_tiddlers = select_relative_attribute('modified', '2009', tiddlers, greater=True)
    assert ['1','c'] == [tiddler.title for tiddler in selected_tiddlers]

def test_custom_select():
    selected_tiddlers = select_by_attribute('year', '2009', tiddlers)
    assert ['1','c'] == [tiddler.title for tiddler in selected_tiddlers]
    selected_tiddlers = select_by_attribute('year', '2000', tiddlers)
    assert [] == [tiddler.title for tiddler in selected_tiddlers]
    selected_tiddlers = select_by_attribute('year', '2009', tiddlers, negate=True)
    assert ['a','b'] == [tiddler.title for tiddler in selected_tiddlers]

def test_field_exists_select():
    selected_tiddlers = select_by_attribute('field', 'index', tiddlers)
    assert ['1','c','a','b'] == [tiddler.title for tiddler in selected_tiddlers]

def test_field_not_exists_select():
    selected_tiddlers = select_by_attribute('field', 'barney', tiddlers, negate=True)
    results = [tiddler.title for tiddler in selected_tiddlers]
    assert ['1','c','a','b'] == results

def test_field_not_exists_empty_select():
    selected_tiddlers = select_by_attribute('field', 'index', tiddlers, negate=True)
    assert [] == [tiddler.title for tiddler in selected_tiddlers]

def test_sorted_field_select():
    selected_tiddlers = select_relative_attribute('index', '2', tiddlers, greater=True)
    assert ['b'] == [tiddler.title for tiddler in selected_tiddlers]

def test_sorted_field_select_no_exist():
    selected_tiddlers = select_relative_attribute('indix', '2', tiddlers, greater=True)
    assert [] == [tiddler.title for tiddler in selected_tiddlers]
