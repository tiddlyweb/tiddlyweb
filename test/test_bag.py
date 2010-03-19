
"""
Test the management of bags and tiddlers in bags.

At the moment these tests are dependent on their order
for the contents of the bag. Which is lame, but useful
in this case.
"""

from tiddlyweb.model.bag import Bag, Policy
from tiddlyweb.model.collections import Tiddlers

import py.test
import copy

def setup_module(module):
    module.bag = Bag(name='foobag')
    from fixtures import tiddlers as tids
# we need to copy tiddlers otherwise the test below which 
# messes with the contents of tiddlers screws with others tests
    module.tiddlers = copy.deepcopy(tids)
    container = Tiddlers()
    container.add(module.tiddlers[0])
    module.bag.tiddlers = container

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

def test_bag_repr():
    bag_repr = '%s' % bag
    assert 'foobag:<tiddlyweb.model.bag.Bag' in bag_repr

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
