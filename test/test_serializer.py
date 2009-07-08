
"""
Confirm the serializer knows how to fail
to load a module.
"""

import py.test

from tiddlyweb.serializer import Serializer

def setup_module(module):
    pass

def test_module_load_fail():
    py.test.raises(ImportError, 'serializer = Serializer("notexistserialization")')

def test_load_module_on_other_path():
    serializer = Serializer("test.other.tiddlyweb.serializations.debug")
    assert type(serializer) == Serializer

def test_wrong_class():
    class Foo(object):
        pass

    foo = Foo()
    serializer = Serializer('text')
    serializer.object = foo
    string = 'haha'

    py.test.raises(AttributeError, 'serializer.to_string()')
    py.test.raises(AttributeError, 'serializer.from_string(string)')



