"""
Make a big data store and see what we learn
from playing with it.
"""

import os

import py.test

import tiddlyweb.stores.text
from tiddlyweb.store import NoBagError
from tiddlyweb.serializer import Serializer
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.recipe import Recipe
from tiddlyweb import control

from fixtures import reset_textstore, muchdata, _teststore

def setup_module(module):
    reset_textstore()
    module.store = _teststore()
    if type(module.store.storage) != tiddlyweb.stores.text.Store:
        py.test.skip('skipping this test for non-text store')
    muchdata(module.store)

def test_many_bags_and_tiddlers():
    """
    Create a bunch of bags and tiddlers.
    """

    assert len(os.listdir('store/bags')) == 30, '30 bags created'
    assert len(os.listdir('store/bags/bag0/tiddlers')) == 10, '10 tiddlers created in a bag'

def test_long_recipe():
    """
    Check muchdata() stored a recipe
    """

    assert os.path.exists('store/recipes/long'), 'long recipe put to disk'

def test_construct_from_recipe():
    """
    Make sure the tiddlywiki that results from
    a recipe has the right stuff in it.
    """

    recipe = Recipe('long')
    recipe = store.get(recipe)

    serializer = Serializer('html')
    serializer.object = recipe
    html_text = serializer.to_string()

    assert 'filter:select=title:tiddler8' in html_text

def test_get_tiddlers_from_bag():
    """
    Make sure a bag comes to life as expected.
    """
    bag = Bag('bag0')
    bag = store.get(bag)

    tiddlers = list(control.get_tiddlers_from_bag(bag))

    assert len(tiddlers) ==  10, 'there are 10 tiddlers in bag0'
    text = ''
    for tiddler in tiddlers:
        store.get(tiddler)
        text += tiddler.text
    assert 'i am tiddler 4' in text

def test_filter_tiddlers_from_bag():
    """
    Make sure a bag comes to life and filters as expect.
    """
    bag = Bag('bag0')
    bag = store.get(bag)

    tiddlers = list(control._filter_tiddlers_from_bag(bag, 'select=tag:tagfour',
        environ={'tiddlyweb.store': store}))
    assert len(tiddlers) == 3
