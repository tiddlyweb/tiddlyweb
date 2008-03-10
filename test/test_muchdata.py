"""
Make a big data store and see what we learn
from playing with it.
"""

import os
import sys
sys.path.append('.')

from tiddlyweb.store import Store, NoBagError
from tiddlyweb.bag import Bag
from tiddlyweb.tiddler import Tiddler
from tiddlyweb.recipe import Recipe
from tiddlyweb import control

from fixtures import reset_textstore

def setup_module(module):
    reset_textstore()
    module.store = Store('text')

def test_many_bags_and_tiddlers():

    for bag_numeral in range(30):
        bag = create_bag(bag_numeral)
        for tiddler_numeral in range(10):
            tiddler = create_tiddler(bag, tiddler_numeral)

    assert len(os.listdir('store/bags')) == 30, '30 bags created'
    assert len(os.listdir('store/bags/bag0/tiddlers')) == 10, '10 tiddlers created in a bag'

def test_long_recipe():

    recipe = Recipe('long')

    recipe_list = []
    for numeral in range(0, 30, 2):
        bag_name = 'bag%s' % numeral
        filter_string = 'tiddler%s' % (numeral % 10)
        if not (numeral % 10) % 3:
            filter_string = filter_string + ' [tag[tag three]]'
        recipe_list.append([bag_name, filter_string])
    recipe.set_recipe(recipe_list)

    store.put(recipe)

    assert os.path.exists('store/recipes/long'), 'long recipe put to disk'

    tiddlers = control.get_tiddlers_from_recipe(recipe, store)
    for tiddler in tiddlers:
        print '%s in %s with content %s' % (tiddler.title, tiddler.bag, tiddler.content)

def create_tiddler(bag, numeral):
    tiddler = Tiddler('tiddler%s' % numeral)
    tiddler.bag = bag.name
    tiddler.content = 'i am tiddler %s' % numeral
    tags = ['basic tag']
    if not numeral % 2:
        tags.append('tagtwo')
    if not numeral % 3:
        tags.append('tagthree')
    if not numeral % 4:
        tags.append('tagfour')
    tiddler.tags = tags
    store.put(tiddler)

def create_bag(numeral):
    bag = Bag('bag%s' % numeral)
    store.put(bag)
    return bag
