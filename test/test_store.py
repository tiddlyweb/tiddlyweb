
"""
Confirm the store knows how to fail
to load a module.
"""

import py.test

from tiddlyweb.config import config
from tiddlyweb.store import Store

from .fixtures import get_store


def test_module_load_fail():
    py.test.raises(ImportError, 'store = Store("notexiststore")')


def test_unsupported_class():

    class Foo(object):
        pass

    foo = Foo()
    store = get_store(config)
    py.test.raises(AttributeError, 'store.put(foo)')
