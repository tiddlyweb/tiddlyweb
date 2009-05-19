
import sys
sys.path.append('.')

from fixtures import reset_textstore, muchdata, teststore
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler

name = u'boom\u00BB\u00BBboom'

def setup_module(module):
    reset_textstore()
    module.store = teststore()
    muchdata(store)

def xtest_simple_search():
    tiddlers = store.search('i am tiddler 0')

    assert len(tiddlers) > 0
    assert type(tiddlers[0]) == Tiddler
    assert tiddlers[0].text is None

def test_unicode_search():

    bag = Bag('bagfoo')
    store.put(bag)

    tiddler = Tiddler(name, bag='bagfoo')
    tiddler.text = name

    store.put(tiddler)

    tiddlers = store.search(name)

    assert len(tiddlers) == 1
