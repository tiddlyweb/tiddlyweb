"""
Start building tests for the concept of a tiddler collection,
which is likely a subclass of a generic collection.

A collection provides:

* way to add a thing
* way to get a hash of the things in it
* way to get stuff out
"""

from tiddlyweb.config import config
from tiddlyweb.model.collections import Collection, Tiddlers
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag

from .fixtures import reset_textstore, get_store


def setup_module(module):
    reset_textstore()
    module.store = get_store(config)


def test_create_collection():
    collection = Collection()
    assert isinstance(collection, Collection)


def test_collection_title():
    collection = Collection(u'barney')
    assert collection.title == u'barney'


def test_add_thing():
    collection = Collection()
    collection.add(u'monkey')
    assert u'monkey' in collection


def test_hash_things():
    collection = Collection()

    collection.add(u'monkey')
    assert u'monkey' in collection

    mdigest = collection.hexdigest()
    assert mdigest

    collection.add(u'cow')
    assert u'cow' in collection

    cdigest = collection.hexdigest()
    assert cdigest
    assert mdigest != cdigest


def test_get_things():
    collection = Collection()
    collection.add(u'monkey')
    collection.add(u'cow')
    all = list(collection)
    assert all == [u'monkey', u'cow']


def test_tiddler_collection():
    tiddlers = Tiddlers()
    n = 4
    for title in [u'how', u'now', u'cow']:
        n = n - 1
        tiddler = Tiddler(title, 'bag')
        tiddler.modified = n
        tiddlers.add(tiddler)
    modified = tiddlers.modified
    assert [u'how', u'now', u'cow'] == list(
            tiddler.title for tiddler in tiddlers)
    assert modified == '30000000000000'


def test_tiddler_racing():

    def race_tiddlers(bag_name, count=2, intitles=['x', 'z'],
            outtitles=['y']):
        bag = Bag(bag_name)
        store.put(bag)
        tiddlers = Tiddlers(store=store)

        for title in ['x', 'y', 'z']:
            tiddler = Tiddler(title, 'foo')
            store.put(tiddler)
            tiddlers.add(tiddler)

        tiddler = Tiddler('y', 'foo')
        store.delete(tiddler)

        tids = list(tiddlers)
        assert len(tids) == count
        for title in intitles:
            assert title in [tid.title for tid in tids]
        for title in outtitles:
            assert title not in [tid.title for tid in tids]

    stored_config = config.get('collections.use_memory')
    config['collections.use_memory'] = False
    race_tiddlers('foo')
    config['collections.use_memory'] = True
    race_tiddlers('bar', count=3, intitles=['x', 'y', 'z'], outtitles=[])
    store.delete(Bag('foo'))
    store.delete(Bag('bar'))
    config['collections.use_memory'] = stored_config


def test_tiddlers_container():
    tiddlers = Tiddlers()

    assert not tiddlers.is_search
    assert not tiddlers.is_revisions
    assert not tiddlers.bag
    assert not tiddlers.recipe

    tiddlers = Tiddlers(bag='foobar')
    assert tiddlers.bag == 'foobar'
    assert not tiddlers.recipe

    tiddlers = Tiddlers(recipe='foobar')
    assert tiddlers.recipe == 'foobar'
    assert not tiddlers.bag
