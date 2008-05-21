
"""
Confirm the store knows how to fail
to load a module.
"""

import sys
sys.path.append('.')

import py.test

from tiddlyweb.store import Store

def setup_module(module):
    pass

def test_module_load_fail():
    py.test.raises(ImportError, 'store = Store("notexiststore")')

