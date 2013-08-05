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


def test_title_fields():
    store.put(Bag('abag'))

    tiddler = Tiddler('one', 'abag')
    tiddler.text = 'hi'
    tiddler.fields = {'title': 'two'}

    assert tiddler.title == 'one'
    assert tiddler.fields['title'] == 'two'

    pytest.raises(TiddlerFormatError, 'store.put(tiddler)')
