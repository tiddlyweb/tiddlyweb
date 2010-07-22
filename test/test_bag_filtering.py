"""
Test that things work correctly when attempting to filter
the contents of a bag.
"""

from tiddlyweb.config import config
from tiddlyweb.filters import parse_for_filters
from tiddlyweb import control

from tiddlywebplugins.utils import get_store

from fixtures import tiddlers, bagfour


def setup_module(module):
    module.environ = {'tiddlyweb.config': config,
            'tiddlyweb.store': get_store(config)}


def xtest_filter_bag_by_filter():
    """
    Confirm a bag will properly filter.
    """

    filtered_tiddlers = list(control.filter_tiddlers_from_bag(bagfour,
        'select=title:TiddlerOne', environ=environ))
    assert len(filtered_tiddlers) == 1
    assert filtered_tiddlers[0].title == 'TiddlerOne'

    filtered_tiddlers = list(control.filter_tiddlers_from_bag(bagfour,
        'select=tag:tagone', environ=environ))
    assert len(filtered_tiddlers) == 2

    filters, thing = parse_for_filters('select=tag:tagone;select=title:TiddlerThree')
    filtered_tiddlers = list(control.filter_tiddlers_from_bag(bagfour,
        filters, environ=environ))
    assert len(filtered_tiddlers) == 1
    assert filtered_tiddlers[0].title == 'TiddlerThree'

