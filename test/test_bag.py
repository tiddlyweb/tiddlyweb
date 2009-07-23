
"""
Test the management of bags and tiddlers in bags.

At the moment these tests are dependent on their order
for the contents of the bag. Which is lame, but useful
in this case.
"""

from tiddlyweb.model.bag import Bag, Policy
from tiddlyweb.model.tiddler import Tiddler

from fixtures import tiddler_source

import py.test
import copy

def test_bag_create():
    """
    Confirm that Bag() requires a name argument.
    """
    py.test.raises(TypeError, "Bag()")

def test_bag_name():
    """
    Confirm the bag gets its name right.
    """

    bag = Bag('foobag')
    assert bag.name == 'foobag', 'the bag should be named foobag'

def test_bag_adjusts_tiddler():
    """
    Confirm adding a tiddler to a bag updates the tiddler object
    notion of its bag.
    """
    bag = Bag('foobag', source=tiddler_source())
    tiddlers = bag.list_tiddlers()
    assert tiddlers[0].bag == 'foobag'

def test_bag_list_tiddlers():
    """
    Confirm the bag is able to list its tiddlers.
    """

    bag = Bag('foobag', source=tiddler_source())
    listed_tiddlers = bag.list_tiddlers()
    assert len(listed_tiddlers) == 4
    assert listed_tiddlers[0].title == 'TiddlerOne'

def test_bag_add_tiddler():
    """
    Confirm adding a tiddler lengthens the bag.
    """

    bag = Bag('foobag', source=tiddler_source())
    bag.add_tiddler(Tiddler('snoop'))
    listed_tiddlers = bag.list_tiddlers()
    assert len(listed_tiddlers) == 5

def test_bag_has_policy():
    """
    Confirm a create bag gets a policy.
    """

    bag = Bag('heartfelt')
    
    assert bag.name == 'heartfelt'
    assert type(bag.policy) == Policy
   
def test_bag_has_description():
    """
    Confirm a bag can set and use a description.
    """

    bag = Bag('hasbeen', desc='monkey puzzle')

    assert bag.name == 'hasbeen'
    assert bag.desc == 'monkey puzzle'

    bag.desc = 'collapsing sideburns'
    assert bag.desc == 'collapsing sideburns'

