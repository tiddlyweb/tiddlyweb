"""
Fields which match tiddler attributes can result
in clobbering those tiddler attributes.
"""

import pytest

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler

from tiddlyweb.serializer import TiddlerFormatError

from fixtures import reset_textstore, _teststore


def setup_module(module):
    reset_textstore()
    module.store = _teststore()


def test_creator():
    store.put(Bag('abag'))

    tiddler = Tiddler('one', 'abag')
    tiddler.text = 'hi'
    tiddler.modifier = 'cdent'
    tiddler.creator = 'sam'
    store.put(tiddler)

    tiddler = store.get(Tiddler('one', 'abag'))

    assert tiddler.modifier == 'cdent'
    assert tiddler.text == 'hi'
    assert tiddler.creator == 'cdent'

    tiddler.modifier = 'sam'
    store.put(tiddler)

    tiddler = store.get(Tiddler('one', 'abag'))

    assert tiddler.modifier == 'sam'
    assert tiddler.text == 'hi'
    assert tiddler.creator == 'cdent'
