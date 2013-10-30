"""
Test using / in names and titles.
"""


from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler

from .fixtures import reset_textstore, _teststore


def setup_module(module):
    reset_textstore()


def test_tiddler_title_with_slash():
    store = _teststore()
    bag = Bag('bag/puss')
    store.put(bag)
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
