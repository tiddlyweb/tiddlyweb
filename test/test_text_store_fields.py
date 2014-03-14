"""
Fields which match tiddler attributes can result
in clobbering those tiddler attributes.
"""

import pytest

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler

from tiddlyweb.serializer import TiddlerFormatError

from .fixtures import reset_textstore, _teststore


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


def test_unicode_field_keys():
    tiddler = Tiddler('two', 'abag')
    tiddler.text = 'hi'
    tiddler.fields = {u'h\u8976': 'two'}

    assert tiddler.fields[u'h\u8976'] == 'two'

    store.put(tiddler)

    tiddler = store.get(Tiddler('two', 'abag'))
    assert tiddler.fields[u'h\u8976'] == 'two'
