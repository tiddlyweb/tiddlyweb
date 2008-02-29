import sys
sys.path.append('.')
from tiddlyweb import filter

from fixtures import tiddlers, bagfour

def test_filter_bag_by_filter():
    """
    Confirm a bag will properly filter.
    """

    filtered_tiddlers = filter.filter_bag(bagfour, filter.by_name, 'TiddlerOne')

    assert len(filtered_tiddlers) == 1, \
            'filtering by name should result in one tiddler, got %s tiddlers' \
            % len(filtered_tiddlers)
    assert filtered_tiddlers[0].name == 'TiddlerOne', \
            'resulting tiddler should be TiddlerOne, is %s' \
            % filtered_tiddlers[0].name

def test_filter_bag_by_filter_string():
    """
    Confirm a bag will properly filter by string.
    """

    filtered_tiddlers = filter.filter_bag(bagfour, '[tag[tagone]]')

    assert len(filtered_tiddlers) == 2, \
            'filtering by name should result in one tiddler, got %s tiddlers' \
            % len(filtered_tiddlers)

    filtered_tiddlers = filter.filter_bag(bagfour, '[tag[tagone]] TiddlerTwo')

    assert len(filtered_tiddlers) == 3, \
            'filtering by name should result in one tiddler, got %s tiddlers' \
            % len(filtered_tiddlers)

