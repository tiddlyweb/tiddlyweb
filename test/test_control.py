"""
Tests for parts of control.py not otherwise covered by
tests.
"""

import py.test

from tiddlyweb.config import config
from tiddlyweb.store import Store, NoBagError
from tiddlyweb.control import (determine_bag_for_tiddler,
        get_tiddlers_from_recipe)
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler


def setup_module(module):
    module.environ = {'tiddlyweb.config': config}
    module.store = Store(config['server_store'][0], config['server_store'][1],
            environ=module.environ)


def test_determine_bag_for_tiddler():
    recipe = Recipe('example')
    recipe.set_recipe([
        ('bagone', ''),
        ('bagtwo', 'select=title:monkey')])

    tiddler = Tiddler('happy')

    bag = determine_bag_for_tiddler(recipe, tiddler)
    assert bag.name == 'bagone'

    tiddler = Tiddler('monkey')
    bag = determine_bag_for_tiddler(recipe, tiddler)
    assert bag.name == 'bagtwo'

    recipe.set_recipe([
        ('bagone', 'select=tag:foo'),
        ('bagtwo', 'select=title:monkeys')])

    py.test.raises(NoBagError, 'determine_bag_for_tiddler(recipe, tiddler)')


def test_bag_object_in_recipe():
    bag = Bag('fwoop')
    store.put(bag)
    tiddler = Tiddler('swell', 'fwoop')
    tiddler.text = 'hi'
    store.put(tiddler)

    recipe = Recipe('heyo')
    recipe.set_recipe([(bag, '')])
    recipe.store = store
    tiddlers = list(get_tiddlers_from_recipe(recipe, environ))
    assert len(tiddlers) == 1
    assert tiddlers[0].title == 'swell'
    assert tiddlers[0].bag == 'fwoop'


