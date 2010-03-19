

from fixtures import reset_textstore, muchdata, _teststore
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler

name = u'boom\u00BB\u00BBboom'

def setup_module(module):
    reset_textstore()
    module.store = _teststore()
    muchdata(store)

def test_simple_search():
    tiddlers = list(store.search('i am tiddler 0'))

    assert len(tiddlers) > 0
    assert type(tiddlers[0]) == Tiddler
    assert tiddlers[0].text is ''

def test_unicode_search():

    bag = Bag(name)
    store.put(bag)

    tiddler = Tiddler('barney', name)
    tiddler.text = name

    store.put(tiddler)

    tiddlers = list(store.search(name))

    assert len(tiddlers) == 1
