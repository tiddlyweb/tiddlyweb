"""
Test that things work correctly when attempting to filter
the contents of a bag.
"""

import sys
sys.path.append('.')
from tiddlyweb import filter
from tiddlyweb import control

from fixtures import tiddlers, bagfour

def test_filter_bag_by_filter():
    """
    Confirm a bag will properly filter.
    """

    filtered_tiddlers = control.filter_tiddlers_from_bag(bagfour, filter.by_title, 'TiddlerOne')

    assert len(filtered_tiddlers) == 1, \
            'filtering by title should result in one tiddler, got %s tiddlers' \
            % len(filtered_tiddlers)
    assert filtered_tiddlers[0].title == 'TiddlerOne', \
            'resulting tiddler should be TiddlerOne, is %s' \
            % filtered_tiddlers[0].title

def test_filter_bag_by_filter_string():
    """
    Confirm a bag will properly filter by string.
    """

    filtered_tiddlers = control.filter_tiddlers_from_bag(bagfour, '[tag[tagone]]')

    assert len(filtered_tiddlers) == 2, \
            'filtering by title should result in one tiddler, got %s tiddlers' \
            % len(filtered_tiddlers)

    filtered_tiddlers = control.filter_tiddlers_from_bag(bagfour, '[tag[tagone]] TiddlerTwo')

    assert len(filtered_tiddlers) == 3, \
            'filtering by title should result in one tiddler, got %s tiddlers' \
            % len(filtered_tiddlers)

