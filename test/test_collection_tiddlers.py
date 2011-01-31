"""
Start building tests for the concept of a tiddler collection,
which is likely a subclass of a generic colleciton.

A collection provides:

* way to add a thing
* way to get a hash of the things in it
* way to get stuff out
"""

from tiddlyweb.config import config
from tiddlyweb.model.collections import Collection, Tiddlers
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag

from tiddlywebplugins.utils import get_store

from fixtures import reset_textstore


def setup_module(module):
    reset_textstore()
    module.store = get_store(config)

def test_create_collection():
    collection = Collection()

    assert isinstance(collection, Collection)

def test_collection_title():
    collection = Collection('barney')

    assert collection.title == 'barney'

def test_add_thing():
    collection = Collection()
    collection.add('monkey')

    assert 'monkey' in collection

def test_hash_things():
    collection = Collection()

    collection.add('monkey')
    assert 'monkey' in collection
    mdigest = collection.hexdigest()
    assert mdigest 

    collection.add('cow')
    assert 'cow' in collection
    cdigest = collection.hexdigest()
    assert cdigest 

    assert mdigest != cdigest

def test_get_things():
    collection = Collection()
    collection.add('monkey')
    collection.add('cow')
    all = list(collection)
    assert all == ['monkey', 'cow']

def test_tiddler_collection():
    tiddlers = Tiddlers()
    n = 4
    for title in ['how', 'now', 'cow']:
        n = n - 1
        tiddler = Tiddler(title, 'bag')
        tiddler.modified = n 
        tiddlers.add(tiddler)
    digest = tiddlers.hexdigest()
    modified = tiddlers.modified
    assert ['how', 'now', 'cow'] == list(tiddler.title for tiddler in tiddlers)
    assert modified == '30000000000000'

def test_tiddler_racing():
    bag = Bag('foo')
    store.put(bag)
    tiddlers = Tiddlers(store=store)

    for title in ['x', 'y', 'z']:
        tiddler = Tiddler(title, 'foo')
        store.put(tiddler)
        tiddlers.add(tiddler)

    tiddler = Tiddler('y', 'foo')
    store.delete(tiddler)

    tids = list(tiddlers)
    assert len(tids) == 2
    assert 'x' in [tiddler.title for tiddler in tids]
    assert 'z' in [tiddler.title for tiddler in tids]
    assert 'y' not in [tiddler.title for tiddler in tids]

