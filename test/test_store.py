"""
Confirm the store knows how to fail
to load a module.
"""

import py.test

from tiddlyweb.config import config
from tiddlyweb.store import Store
from tiddlyweb.web.http import HTTP403
from fixtures import _teststore, bagone, bagtwo, bagthree, bagfour


def setup_module(module):
    module.store = _teststore()
    for bag in [bagone, bagtwo, bagthree, bagfour]:
        store.put(bag)

def test_module_load_fail():
    py.test.raises(ImportError, 'store = Store("notexiststore")')

def test_unsupported_class():
    class Foo(object):
        pass

    foo = Foo()
    store = Store(config['server_store'][0], environ={'tiddlyweb.config': config})
    py.test.raises(AttributeError, 'store.put(foo)')

def test_insecure_access():
    insecure_environ = {
        'wsgi.url_scheme': 'http',
        'tiddlyweb.config': {
            'secure_bags': ['bagtwo', 'bagfour']
        }
    }
    store.environ.update(insecure_environ)

    assert store.put(bagone) == None
    assert store.put(bagthree) == None
    py.test.raises(HTTP403, 'store.put(bagtwo)')
    py.test.raises(HTTP403, 'store.put(bagfour)')

    assert store.get(bagone)
    assert store.get(bagthree)
    py.test.raises(HTTP403, 'store.get(bagtwo)')
    py.test.raises(HTTP403, 'store.get(bagfour)')

    assert store.delete(bagone) == None
    assert store.delete(bagthree) == None
    py.test.raises(HTTP403, 'store.delete(bagtwo)')
    py.test.raises(HTTP403, 'store.delete(bagfour)')

def test_secure_access():
    secure_environ = {
        'wsgi.url_scheme': 'https',
        'tiddlyweb.config': {
            'secure_bags': ['bagtwo', 'bagfour']
        }
    }
    store.environ.update(secure_environ)

    assert store.put(bagone) == None
    assert store.put(bagtwo) == None
    assert store.put(bagthree) == None
    assert store.put(bagfour) == None

    assert store.get(bagone)
    assert store.get(bagtwo)
    assert store.get(bagthree)
    assert store.get(bagfour)

    assert store.delete(bagone) == None
    assert store.delete(bagtwo) == None
    assert store.delete(bagthree) == None
    assert store.delete(bagfour) == None
