"""
Tests for parts of control.py not otherwise covered by
tests.
"""

import py.test

from tiddlyweb.config import config
from tiddlyweb.store import Store, NoBagError
from tiddlyweb.control import (determine_bag_for_tiddler,
        get_tiddlers_from_recipe, determine_bag_from_recipe,
        readable_tiddlers_by_bag)
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler


def setup_module(module):
    module.environ = {'tiddlyweb.config': config}
    module.store = Store(config['server_store'][0], config['server_store'][1],
            environ=module.environ)
    module.environ['tiddlyweb.store'] = module.store


def teardown_module(module):
    del config['indexer']


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


def test_index_query_in_recipe():
    config['indexer'] = 'test.indexernot'

    bag = Bag('noop')
    store.put(bag)
    tiddler = Tiddler('dwell', 'noop')
    store.put(tiddler)

    recipe = Recipe('coolio')
    recipe.set_recipe([('noop', ''), ('fwoop','')])
    recipe.store = store

    tiddler = Tiddler('swell')
    py.test.raises(ImportError,
            'determine_bag_from_recipe(recipe, tiddler, environ)')

    config['indexer'] = 'test.indexer'
    bag = determine_bag_from_recipe(recipe, tiddler, environ)
    assert bag.name == 'fwoop'

    tiddler = Tiddler('dwell')
    bag = determine_bag_from_recipe(recipe, tiddler, environ)
    assert bag.name == 'noop'

    tiddler = Tiddler('carnaby') # nowhere
    py.test.raises(NoBagError,
            'determine_bag_from_recipe(recipe, tiddler, environ)')


def test_readable_tiddlers_by_bag():
    bagone = Bag('cdentread')
    bagone.policy.read = ['cdent']
    store.put(bagone)
    bagtwo = Bag('fndread')
    bagtwo.policy.read = ['fnd']
    store.put(bagtwo)
    bagthree = Bag('allread')
    store.put(bagthree)

    count = 0
    tiddlers = []
    for bag in ['cdent', 'fnd', 'all', 'cdent', 'fnd', 'all', 'notreal']:
        count += 1
        tiddler = Tiddler('tiddler%s' % count, '%sread' % bag)
        tiddler.text = 'narf'
        tiddlers.append(tiddler)

    usersign = {'name': 'cdent', 'roles': []}
    readable = list(readable_tiddlers_by_bag(store, tiddlers, usersign))
    assert (['tiddler1', 'tiddler3', 'tiddler4', 'tiddler6', 'tiddler7'] ==
            [tiddler.title for tiddler in readable])

    usersign = {'name': 'fnd', 'roles': []}
    readable = list(readable_tiddlers_by_bag(store, tiddlers, usersign))
    assert (['tiddler2', 'tiddler3', 'tiddler5', 'tiddler6', 'tiddler7'] ==
            [tiddler.title for tiddler in readable])

    usersign = {'name': 'GUEST', 'roles': []}
    readable = list(readable_tiddlers_by_bag(store, tiddlers, usersign))
    assert (['tiddler3', 'tiddler6', 'tiddler7'] ==
            [tiddler.title for tiddler in readable])
