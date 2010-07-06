"""
Test using / in names and titles.
"""


import os

from fixtures import reset_textstore, _teststore

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler

def setup_module(module):
    reset_textstore()
    module.store = _teststore()
    module.bag = Bag('bag/puss')
    module.store.put(module.bag)

def test_tiddler_title_with_slash():
    tiddler = Tiddler('hello/monkey')
    tiddler.bag = u'bag/puss'
    tiddler.text = 'artifice'

    assert tiddler.title == 'hello/monkey'

    store.put(tiddler)

    tiddler2 = Tiddler('hello/monkey')
    tiddler2.bag = u'bag/puss'

    tiddler2 = store.get(tiddler2)

    assert tiddler2.title == 'hello/monkey'
    assert tiddler2.text == 'artifice'


