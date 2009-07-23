
from tiddlyweb.model.bag import Bag


def test_simple_bag():
    bag = Bag('tester')
    bag.add_tiddler_source(i for i in [1,2,3])
    tiddlers = list(bag.tiddlers)
    assert tiddlers == [1,2,3]
    tiddlers = bag.list_tiddlers()
    assert tiddlers == [1,2,3]
    tiddlers = bag.list_tiddlers()
    assert tiddlers == [1,2,3]

def test_expanding_bag():
    bag = Bag('tester')
    bag.add_tiddler_source(i for i in [1,2,3])
    bag.add_tiddler_source(i for i in ['a','b','c'])
    tiddlers = bag.tiddlers
    assert tiddlers.next() == 1
    assert tiddlers.next() == 2
    assert tiddlers.next() == 3
    assert tiddlers.next() == 'a'
    assert tiddlers.next() == 'b'
    assert tiddlers.next() == 'c'

def test_listing_half_bag():
    bag = Bag('tester')
    bag.add_tiddler_source(i for i in [1,2,3])
    tiddlers = bag.tiddlers
    assert tiddlers.next() == 1
    list(tiddlers) # force gen to unwind
    tiddlers = bag.list_tiddlers()
    assert tiddlers == [1,2,3]

def test_add_one():
    """
    Set up a multi source of just one tiddler in each source.
    """
    bag = Bag('tester')
    bag.add_tiddler(1)
    bag.add_tiddler(2)
    bag.add_tiddler(3)
    bag.add_tiddler(4)
    bag.add_tiddler(5)
    tiddlers = bag.tiddlers
    assert tiddlers.next() == 1
    assert tiddlers.next() == 2
    assert tiddlers.next() == 3
    assert tiddlers.next() == 4
    assert tiddlers.next() == 5

# TODO: need a test for a recipe with the same bag in it multiple times...
