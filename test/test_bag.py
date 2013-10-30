
"""
Test the basics of bags.
"""

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import Policy

import py.test


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
    assert bag.name == 'foobag'
    bag_repr = '%s' % bag
    assert 'foobag:<tiddlyweb.model.bag.Bag' in bag_repr


def test_bag_has_policy():
    """
    Confirm a created bag gets a policy.
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
