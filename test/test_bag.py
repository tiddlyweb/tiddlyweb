
"""
Test the management of bags and tiddlers in bags.

At the moment these tests are dependent on their order
for the contents of the bag. Which is lame, but useful
in this case.
"""

from tiddlyweb.model.bag import Bag, Policy

import py.test
import copy

def setup_module(module):
    module.bag = Bag(name='foobag')
    from fixtures import tiddlers as tids
# we need to copy tiddlers otherwise the test below which 
# messes with the contents of tiddlers screws with others tests
    module.tiddlers = copy.deepcopy(tids)
    module.bag.add_tiddler_source(tiddler for tiddler in [module.tiddlers[0]])

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

def test_bag_adjusts_tiddler():
    """
    Confirm adding a tiddler to a bag updates the tiddler object
    notion of its bag.
    """
    tiddlers = bag.list_tiddlers()
    assert tiddlers[0].bag == 'foobag'

def test_bag_list_tiddlers():
    """
    Confirm the bag is able to list its tiddlers.
    """

    listed_tiddlers = bag.list_tiddlers()
    assert len(listed_tiddlers) == 1
    assert listed_tiddlers[0].title == tiddlers[0].title

def test_bag_add_tiddler():
    """
    Confirm adding a tiddler lengthens the bag.
    """

    bag.add_tiddler(tiddlers[1])
    x = bag.list_tiddlers() # run the gen off its end
    listed_tiddlers = bag.list_tiddlers()
    assert len(listed_tiddlers) == 2

def test_bag_add_duplicate():
    """
    Confirm adding the same tiddler does not lengthen bag.
    """

    bag.add_tiddler(tiddlers[0])
    x = bag.list_tiddlers() # run the gen off its end
    listed_tiddlers = bag.list_tiddlers()
    assert len(listed_tiddlers) == 2

def xtest_store_by_copy():
    """
    Confirm tiddlers in bag are copies, not references.
    """

    tiddlers[0].text = 'changed it'
    tiddlers[0].bag = bag.name

    assert tiddlers[0].text != bag[tiddlers[0]].text, 'tiddlers in bag are copies not reference'

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

