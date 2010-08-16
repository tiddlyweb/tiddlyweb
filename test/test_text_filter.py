"""
Tests for a [text[<string>]] style filter.
"""


from tiddlyweb import control
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag

from fixtures import muchdata, reset_textstore, _teststore

def setup_module(module):
    reset_textstore()
    module.store = _teststore()
    muchdata(module.store)

def test_filter_by_text():
    bag = Bag('bag0')
    bag = store.get(bag)

    bags_tiddlers = list(store.list_bag_tiddlers(bag))
    assert len(bags_tiddlers) == 10

    found_tiddlers = list(control._filter_tiddlers_from_bag(
        bag, 'select=text:tiddler 0',
        environ={'tiddlyweb.store': store}))
    assert len(found_tiddlers) == 1
    assert found_tiddlers[0].title == 'tiddler0'

def test_filter_by_text_string():
    bag = Bag('bag0')
    bag = store.get(bag)

    bags_tiddlers = list(store.list_bag_tiddlers(bag))
    assert len(bags_tiddlers) == 10

    found_tiddlers = list(control._filter_tiddlers_from_bag(
        bag, 'select=text:tiddler 0',
        environ={'tiddlyweb.store': store}))
    assert len(found_tiddlers) == 1
    assert found_tiddlers[0].title == 'tiddler0'

def test_filter_by_text_string_negate():
    bag = Bag('bag0')
    bag = store.get(bag)

    bags_tiddlers = list(store.list_bag_tiddlers(bag))
    assert len(bags_tiddlers) == 10

    found_tiddlers = list(control._filter_tiddlers_from_bag(bag,
        'select=text:!tiddler 0',
        environ={'tiddlyweb.store': store}))
    assert len(found_tiddlers) == 9
