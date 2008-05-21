
"""
Confirm the serializer knows how to fail
to load a module.
"""

import sys
sys.path.append('.')

import py.test

from tiddlyweb.serializer import Serializer

def setup_module(module):
    pass

def test_module_load_fail():
    py.test.raises(ImportError, 'serializer = Serializer("notexistserialization")')

