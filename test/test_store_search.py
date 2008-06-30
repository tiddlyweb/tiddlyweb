
import sys
sys.path.append('.')

from fixtures import reset_textstore, muchdata
from tiddlyweb.store import Store
from tiddlyweb.tiddler import Tiddler

def setup_module(module):
    reset_textstore()
    store = Store('text')
    muchdata(store)

def test_simple_search():
    store = Store('text')

    tiddlers = store.search('i am tiddler 0')

    assert len(tiddlers) > 0
    assert type(tiddlers[0]) == Tiddler
    assert tiddlers[0].text is None

