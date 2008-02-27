
"""
Test the management of bags and tiddlers in bags.

At the moment these tests are dependent on their order
for the contents of the bag. Which is lame, but useful
in this case.
"""

import sys
sys.path.append('.')
from tiddlyweb.bag import Bag

import py.test

tiddlers = [
        {
            'name': 'TiddlerOne',
            'content': 'tiddler one content',
            'tags': ['tagone', 'tagtwo']
        },
        {
            'name': 'TiddlerTwo',
            'content': 'tiddler two content',
            'tags': []
        },
        {
            'name': 'TiddlerThree',
            'content': 'tiddler three content',
            'tags': ['tagone', 'tagthree']
        }
]

def setup_module(module):
    module.bag = Bag(name='foobag')
    module.bag.add_tiddler(tiddlers[0])

def test_bag_create():
    """
    Confirm that Bag() requires a name argument.
    """
    py.test.raises(TypeError, "Bag()")

def test_bag_name():
    """
    Confirm the bag gets its name right.
    """

    assert bag.name == 'foobag', 'the bag should be named foobag'

def test_bag_list_tiddlers():
    """
    Confirm the bag is able to list its tiddlers.
    """

    listed_tiddlers = bag.list_tiddlers()
    assert len(bag) == 1, 'the bag should be the length of the tiddlers, 1, is %s' % len(bag)
    assert len(listed_tiddlers) == 1, 'there should be 1 tiddler in the bag, is %s' % len(listed_tiddlers)
    assert listed_tiddlers[0]['name'] == tiddlers[0]['name'], 'tiddler in bag is tiddler put in bag'

def test_bag_add_tiddler():
    """
    Confirm adding a tiddler lengthens the bag.
    """

    bag.add_tiddler(tiddlers[1])
    listed_tiddlers = bag.list_tiddlers()
    assert len(bag) == 2, 'the bag should now be length 2, is %s' % len(bag)
    assert len(listed_tiddlers) == 2, 'there should be 2 tiddlers in the bag, is %s' % len(listed_tiddlers)

def test_bag_add_duplicate():
    """
    Confirm adding the same tiddler does not lengthen bag.
    """

    bag.add_tiddler(tiddlers[0])
    listed_tiddlers = bag.list_tiddlers()
    assert len(bag) == 2, 'the bag should be length 2 after adding same tiddler, is %s' % len(bag)
    assert len(listed_tiddlers) == 2, 'there should be 2 tiddlers in the bag after adding same tiddler, is %s' % len(listed_tiddlers)

def test_store_by_copy():
    """
    Confirm tiddlers in bag are copies, not references.
    """

    tiddlers[0]['content'] = 'changed it'

    assert tiddlers[0]['content'] != bag[tiddlers[0]]['content'], 'tiddlers in bag are copies not reference'

def test_filter_bag_by_filter():
    """
    Confirm a bag will properly filter.
    """

    from tiddlyweb import filter

    filtered_tiddlers = bag.filter_tiddlers(filter.by_name, 'TiddlerOne')

    assert len(filtered_tiddlers) == 1, 'filtering by name should result in one tiddler, got %s tiddlers' % len(filtered_tiddlers)
    assert filtered_tiddlers[0]['name'] == 'TiddlerOne', 'resulting tiddler should be TiddlerOne, is %s' % filtered_tiddlers[0]['name']

def test_filter_bag_by_filter_string():
    """
    Confirm a bag will properly filter by string.
    """

    filtered_tiddlers = bag.filter_tiddlers('[tag[tagone]]')

    assert len(filtered_tiddlers) == 1, 'filtering by name should result in one tiddler, got %s tiddlers' % len(filtered_tiddlers)
    assert filtered_tiddlers[0]['name'] == 'TiddlerOne', 'resulting tiddler should be TiddlerOne, is %s' % filtered_tiddlers[0]['name']

    bag.add_tiddler(tiddlers[2])
    filtered_tiddlers = bag.filter_tiddlers('[tag[tagone]]')

    assert len(filtered_tiddlers) == 2, 'filtering by name should result in one tiddler, got %s tiddlers' % len(filtered_tiddlers)

def test_bag_remove():
    """
    Confirm the bag shrinks when you remove a tiddler.
    """

    assert len(bag) == 3, 'before removing a tiddler bag is len 3, bag size now %s' % len(bag)
    bag.remove_tiddler(tiddlers[2])
    assert len(bag) == 2, 'removing a tiddler shrinks the bag to 2, bag size now %s' % len(bag)

# trying to remove a tiddler that's not there gives a KeyError
    py.test.raises(KeyError, "bag.remove_tiddler(tiddlers[2])")
