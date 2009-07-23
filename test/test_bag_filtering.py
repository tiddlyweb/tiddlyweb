"""
Test that things work correctly when attempting to filter
the contents of a bag.
"""

from tiddlyweb.filters import parse_for_filters
from tiddlyweb import control
from tiddlyweb.model.bag import Bag

from fixtures import tiddler_source

def test_filter_bag_by_filter():
    """
    Confirm a bag will properly filter.
    """

    bagfour = Bag('four', source=tiddler_source())
    # tiddler_source has two tiddlers named TiddlerOne in it
    filtered_tiddlers = list(control.filter_tiddlers_from_bag(bagfour, 'select=title:TiddlerOne'))

    assert len(filtered_tiddlers) == 2
    assert filtered_tiddlers[0].title == 'TiddlerOne'

    bagfour = Bag('four', source=tiddler_source())
    filtered_tiddlers = list(control.filter_tiddlers_from_bag(bagfour, 'select=tag:tagone'))
    assert len(filtered_tiddlers) == 3

    bagfour = Bag('four', source=tiddler_source())
    filters, thing = parse_for_filters('select=tag:tagone;select=title:TiddlerThree')
    filtered_tiddlers = list(control.filter_tiddlers_from_bag(bagfour, filters))
    assert len(filtered_tiddlers) == 1
    assert filtered_tiddlers[0].title == 'TiddlerThree'
