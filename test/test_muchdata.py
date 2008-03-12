"""
Make a big data store and see what we learn
from playing with it.
"""

import os
import sys
sys.path.append('.')

from tiddlyweb.store import Store, NoBagError
from tiddlyweb.serializer import Serializer
from tiddlyweb.bag import Bag
from tiddlyweb.tiddler import Tiddler
from tiddlyweb.recipe import Recipe
from tiddlyweb import control
from tiddlyweb import filter

from fixtures import reset_textstore

def setup_module(module):
    reset_textstore()
    module.store = Store('text')

def test_many_bags_and_tiddlers():
    """
    Create a bunch of bags and tiddlers.
    """

    for bag_numeral in range(30):
        bag = create_bag(bag_numeral)
        for tiddler_numeral in range(10):
            tiddler = create_tiddler(bag, tiddler_numeral)

    assert len(os.listdir('store/bags')) == 30, '30 bags created'
    assert len(os.listdir('store/bags/bag0/tiddlers')) == 10, '10 tiddlers created in a bag'

def test_long_recipe():
    """
    Store a long recipe.
    """

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

def test_construct_from_recipe():
    """
    Make sure the tiddlywiki that results from
    a recipe has the right stuff in it.
    """

    recipe = Recipe('long')
    store.get(recipe)

    serializer = Serializer(recipe, 'wiki')
    wiki_text = serializer.to_string()

    assert 'i am tiddler 8' in wiki_text, 'wiki contains tiddler 8'

def test_get_tiddlers_from_bag():
    """
    Make sure a bag comes to life as expected.
    """
    bag = Bag('bag0')
    store.get(bag)

    tiddlers = control.get_tiddlers_from_bag(bag)

    assert len(tiddlers) ==  10, 'there are 10 tiddlers in bag0'
    content = ''
    for tiddler in tiddlers:
        content += tiddler.content
    assert 'i am tiddler 4' in content, 'we got some of the right content'

def test_filter_tiddlers_from_bag():
    """
    Make sure a bag comes to life and filters as expect.
    """
    bag = Bag('bag0')
    store.get(bag)

    tiddlers = control.filter_tiddlers_from_bag(bag, '[tag[tagfour]]')
    assert len(tiddlers) == 3, 'there are 3 tiddlers when filters on tagfour'

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
