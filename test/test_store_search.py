
import sys
sys.path.append('.')

from fixtures import reset_textstore, muchdata, teststore
from tiddlyweb.model.tiddler import Tiddler

name = u'boom\u00BB\u00BBboom'

def setup_module(module):
    reset_textstore()
    module.store = teststore()
    muchdata(store)

def test_simple_search():
    tiddlers = store.search('i am tiddler 0')

    assert len(tiddlers) > 0
    assert type(tiddlers[0]) == Tiddler
    assert tiddlers[0].text is None

def test_unicode_search():
    tiddler = Tiddler(name, bag='bag0')
    tiddler.text = name

    store.put(tiddler)

    tiddlers = store.search(name)

    assert len(tiddlers) == 1
