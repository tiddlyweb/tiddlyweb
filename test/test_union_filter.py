
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.filters.select import mselect


tiddlers = [Tiddler('1'), Tiddler('c'), Tiddler('a'), Tiddler('b')]

def test_simple_mselect():
    selected_tiddlers = mselect('title:1,title:c', tiddlers)
    assert ['1','c'] == [tiddler.title for tiddler in selected_tiddlers]

