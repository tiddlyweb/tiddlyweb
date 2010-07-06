"""
Store and retrieve a bag.

See about doing this lazily.
"""

import os

import py.test

import tiddlyweb.stores.text

from fixtures import tiddlers, bagone, reset_textstore, _teststore
from tiddlyweb.store import NoBagError
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler

def setup_module(module):
    reset_textstore()
    module.store = _teststore()

def test_simple_put():
    bagone.desc = 'I enjoy being stored'
    store.put(bagone)

    if type(store.storage) != tiddlyweb.stores.text.Store:
        py.test.skip('skipping this test for non-text store')

    assert os.path.exists('store/bags/bagone'), \
            'path %s should be created' \
            % 'store/bags/bagone'
    assert os.path.exists('store/bags/bagone/policy'), \
            'path %s should be created' \
            % 'store/bags/bagone/policy'
    assert os.path.exists('store/bags/bagone/description'), \
            'path %s should be created' \
            % 'store/bags/bagone/description'
    assert os.path.exists('store/bags/bagone/tiddlers'), \
            'path %s should be created' \
            % 'store/bags/bagone/tiddlers'

def test_simple_get():

    tiddler = tiddlers[0]
    tiddler.bag = u'bagone'
    store.put(tiddler)

    bag = Bag(name='bagone')
    bag = store.get(bag)

    the_tiddler = store.list_bag_tiddlers(bag).next()
    assert bag.policy.read == bagone.policy.read
    assert bag.policy.write == bagone.policy.write
    assert bag.policy.create == bagone.policy.create
    assert bag.policy.delete == bagone.policy.delete
    assert bag.policy.manage == bagone.policy.manage
    assert bag.policy.owner == bagone.policy.owner
    assert bag.desc == 'I enjoy being stored'
    
    the_tiddler = store.get(the_tiddler)
    assert the_tiddler.title == tiddler.title
    assert sorted(the_tiddler.tags) == sorted(tiddler.tags)

def test_failed_get():
    bag = Bag(name='bagnine')
    py.test.raises(NoBagError, 'store.get(bag)')

def test_delete():
    bag = Bag('deleteme')
    bag.desc = 'delete me please'
    store.put(bag)

    stored_bag = Bag('deleteme')
    stored_bag = store.get(stored_bag)
    assert stored_bag.desc == 'delete me please'

    deleted_bag = Bag('deleteme')
    store.delete(deleted_bag)

    py.test.raises(NoBagError, 'store.get(deleted_bag)')
    py.test.raises(NoBagError, 'store.delete(deleted_bag)')

def test_list():
    bag = Bag('bagtwo')
    store.put(bag)
    bags = list(store.list_bags())

    assert len(bags) == 2
    assert u'bagone' in [bag.name for bag in bags]
    assert u'bagtwo' in [bag.name for bag in bags]
