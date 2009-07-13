"""
Test that things work correctly when attempting to filter
the contents of a bag.
"""

from tiddlyweb.filters import parse_for_filters
from tiddlyweb import control

from fixtures import tiddlers, bagfour

def test_filter_bag_by_filter():
    """
    Confirm a bag will properly filter.
    """

    filtered_tiddlers = list(control.filter_tiddlers_from_bag(bagfour, 'select=title:TiddlerOne'))

    assert len(filtered_tiddlers) == 1
    assert filtered_tiddlers[0].title == 'TiddlerOne'

    filtered_tiddlers = list(control.filter_tiddlers_from_bag(bagfour, 'select=tag:tagone'))
    assert len(filtered_tiddlers) == 2

    filters, thing = parse_for_filters('select=tag:tagone;select=title:TiddlerThree')
    filtered_tiddlers = list(control.filter_tiddlers_from_bag(bagfour, filters))
    assert len(filtered_tiddlers) == 1
    assert filtered_tiddlers[0].title == 'TiddlerThree'

