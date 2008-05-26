"""
Store and retrieve a bag.

See about doing this lazily.
"""

import os
import sys
sys.path.append('.')

import py.test

from fixtures import tiddlers, bagone, reset_textstore
from tiddlyweb.store import Store, NoBagError
from tiddlyweb.bag import Bag
from tiddlyweb.tiddler import Tiddler

def setup_module(module):
    reset_textstore()

def test_simple_put():
    store = Store('text')
    store.put(bagone)

    assert os.path.exists('store/bags/bagone'), \
            'path %s should be created' \
            % 'store/bags/bagone'
    assert os.path.exists('store/bags/bagone/policy'), \
            'path %s should be created' \
            % 'store/bags/bagone/policy'
    assert os.path.exists('store/bags/bagone/tiddlers'), \
            'path %s should be created' \
            % 'store/bags/bagone/tiddlers'

def test_simple_get():

    store = Store('text')
    tiddler = tiddlers[0]
    tiddler.bag = 'bagone'
    store.put(tiddler)

    bag = Bag(name='bagone')
    store.get(bag)

    assert bag.list_tiddlers()[0].title == tiddler.title, 'stored tiddler title and retrieved tiddler.title the same'
    assert bag.list_tiddlers()[0].text == None
    assert bag.list_tiddlers()[0].tags == []
    assert bag.policy.read == bagone.policy.read
    assert bag.policy.write == bagone.policy.write
    assert bag.policy.create == bagone.policy.create
    assert bag.policy.delete == bagone.policy.delete
    assert bag.policy.manage == bagone.policy.manage
    assert bag.policy.owner == bagone.policy.owner
    
    the_tiddler = bag.list_tiddlers()[0]
    store.get(the_tiddler)
    assert the_tiddler.title == tiddler.title, 'stored tiddler title and retrieved tiddler.title the same'
    assert sorted(the_tiddler.tags) == sorted(tiddler.tags)

def test_failed_get():
    store = Store('text')
    bag = Bag(name='bagnine')
    py.test.raises(NoBagError, 'store.get(bag)')

