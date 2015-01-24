"""
TiddlyWiki5 has tiddler dicitionary tiddlers, that look like this:

    a:one
    b:two
    c:three

and have type/x-tiddler-dictionary.

See: http://tiddlywiki.com/static/DataTiddlers.html
"""


from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag

from .fixtures import reset_textstore, _teststore

TYPE = 'application/x-tiddler-dictionary'

TEXT = """a:one
b:two
c:three"""


def setup_module(module):
    reset_textstore()
    module.store = _teststore()


def test_tiddler_dictionary():
    bag = Bag('bagone')
    store.put(bag)
    tiddler = Tiddler('dictionary', 'bagone')
    tiddler.text = TEXT
    tiddler.type = TYPE
    store.put(tiddler)

    tiddler = store.get(Tiddler('dictionary', 'bagone'))
    assert tiddler.text == TEXT
    assert tiddler.type == TYPE
