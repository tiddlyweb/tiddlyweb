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

from fixtures import reset_textstore, muchdata

def setup_module(module):
    reset_textstore()
    module.store = Store('text')
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

