"""
Flow through the entire process we might have.

* someone sends in a tiddler to be saved in a
  bag, thinking the bag exists
  * the bag is not there, throw something
* create a bag and store it
* store that tiddler
* get it back
* diddle it
* store it again, different bag

* someone has a tiddler, but doesn't
  know where it goes
  * find the proper bag via recipe
* save to the bag
* retrieve it again
"""

import os

import tiddlyweb.stores.text
from tiddlyweb.store import NoBagError
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.recipe import Recipe
from tiddlyweb import control

from fixtures import reset_textstore, recipe_list, _teststore

import py.test

def setup_module(module):
    reset_textstore()
    module.store = _teststore()
    if type(module.store.storage) != tiddlyweb.stores.text.Store:
        py.test.skip('skipping this test for non-text store')

def test_no_bag_for_tiddler():
    tiddler = Tiddler(title='testnobag')
    tiddler.text = 'no bag here'
    tiddler.bag = u'no bag of this name'

    py.test.raises(NoBagError, "store.put(tiddler)")

def test_put_and_get_tiddler():
    tiddler = Tiddler(title='testbag')
    tiddler.text = 'bag1 here'
    bag = Bag(name = 'bag1')
    tiddler.bag = u'bag1'

    store.put(bag)
    store.put(tiddler)

    new_tiddler = Tiddler(title='testbag')
    new_tiddler.bag = u'bag1'
    new_tiddler = store.get(new_tiddler)

    assert new_tiddler.text == 'bag1 here'

def test_get_diddle_put_tiddler():
    new_tiddler = Tiddler(title='testbag')
    new_tiddler.bag = u'bag1'
    new_tiddler = store.get(new_tiddler)

    new_tiddler.bag = u'bag2'
    new_tiddler.text = 'bag2 here'

    py.test.raises(NoBagError, "store.put(new_tiddler)")

    bag = Bag('bag2')
    store.put(bag)

    store.put(new_tiddler)

    assert os.path.exists('store/bags/bag2/tiddlers/testbag')
    assert os.path.exists('store/bags/bag1/tiddlers/testbag')

def test_tiddler_unique_by_bags():
    tiddler_one = Tiddler('testbag')
    tiddler_one.bag = 'bag1'
    tiddler_two = Tiddler('testbag')
    tiddler_two.bag = 'bag2'

    assert tiddler_one.text == tiddler_two.text == '', \
            'empty tiddlers have equally empty content'

    tiddler_one = store.get(tiddler_one)
    tiddler_two = store.get(tiddler_two)

    assert tiddler_one.text != tiddler_two.text, \
            'empty tiddlers have different content'

def test_put_recipe():
    recipe = Recipe('cookies')
    recipe.set_recipe(recipe_list)

    store.put(recipe)

    assert os.path.exists('store/recipes/cookies')

def test_where_this_tiddler():
    """
    recipe bag determination presumes there is a tiddler of the same name
    already in the bag. Is this right or not? Seems like maybe we want to 
    put the bag in the collection if it matches the filter stream.
    """
    tiddler_lonely = Tiddler('TiddlerOne')
    tiddler_lonely.text = 'tiddlerincookiesyay'

    recipe = Recipe('cookies')
    recipe = store.get(recipe)

    bag = control.determine_bag_for_tiddler(recipe, tiddler_lonely)

    assert bag.name == 'bagone'

    tiddler_lonely.bag = bag.name
    try:
        store.put(tiddler_lonely)
    except NoBagError:
        store.put(bag)
        store.put(tiddler_lonely)

    assert os.path.exists('store/bags/bagone/tiddlers/TiddlerOne')

