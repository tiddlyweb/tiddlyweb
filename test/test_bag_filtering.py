"""
Test that things work correctly when attempting to filter
the contents of a bag.
"""

from tiddlyweb.config import config
from tiddlyweb.filters import parse_for_filters
from tiddlyweb import control
from tiddlyweb.model.bag import Bag

from tiddlywebplugins.utils import get_store

from fixtures import reset_textstore, tiddlers


def setup_module(module):
    reset_textstore()
    module.store = get_store(config)
    module.environ = {'tiddlyweb.config': config,
            'tiddlyweb.store': module.store}


def test_filter_bag_by_filter():
    """
    Confirm a bag will properly filter.
    """

    bagfour = Bag('bagfour')
    store.put(bagfour)
    bagfour.store = store
    for tiddler in tiddlers:
        tiddler.bag = 'bagfour'
        store.put(tiddler)

    filtered_tiddlers = list(control._filter_tiddlers_from_bag(bagfour,
        'select=title:TiddlerOne', environ=environ))
    assert len(filtered_tiddlers) == 1
    assert filtered_tiddlers[0].title == 'TiddlerOne'

    filtered_tiddlers = list(control._filter_tiddlers_from_bag(bagfour,
        'select=tag:tagone', environ=environ))
    assert len(filtered_tiddlers) == 2

    filters, thing = parse_for_filters(
            'select=tag:tagone;select=title:TiddlerThree', environ=environ)
    filtered_tiddlers = list(control._filter_tiddlers_from_bag(bagfour,
        filters, environ=environ))
    assert len(filtered_tiddlers) == 1
    assert filtered_tiddlers[0].title == 'TiddlerThree'
