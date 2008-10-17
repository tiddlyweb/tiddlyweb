
"""
Test a recipe to confirm it does all its recipe
things.
"""

import sys
sys.path.append('.')

import py.test

from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import NoBagError
from tiddlyweb import control

from fixtures import tiddlers, bagone, bagtwo, bagthree, bagfour, recipe_list

def setup_module(module):
    module.recipe = Recipe(name='foorecipe')

def test_recipe_name():
    assert recipe.name == 'foorecipe', 'our recipe gets its name right'

def test_set_recipe():
    """
    Confirm setting the recipe to the contents of a list.
    """
    recipe.set_recipe(recipe_list)
    assert len(recipe) == 3, 'length of recipe should be 3 is %s' % len(recipe)

def test_recipe_has_description():
    """
    Confirm a recipe can set and use a description.
    """

    recipe = Recipe('hasbeen', desc='monkey puzzle')

    assert recipe.name == 'hasbeen'
    assert recipe.desc == 'monkey puzzle'

    recipe.desc = 'collapsing sideburns'
    assert recipe.desc == 'collapsing sideburns'

def test_get_recipe_list():
    """
    Get a representation of the recipe, a list of bag + filter URLs.

    Note that you can just use the object itself if you want.
    """
    rlist = recipe.get_recipe()
    assert rlist == recipe_list, 'stored list should be same as given list'

def test_get_tiddlers():
    """
    Get all the tiddlers produced by this recipe.
    """

    tiddlers = control.get_tiddlers_from_recipe(recipe)
    assert len(tiddlers) == 3, 'tiddler list should be length 3, is %s' % len(tiddlers)

def test_get_tiddlers_limited():
    """
    Using a different recipe get different tiddlers.
    """

    short_recipe = Recipe(name='foobar')
    short_recipe.set_recipe([
        [bagone, ''],
        [bagfour, '[tag[tagone]]']
        ])
    tiddlers = control.get_tiddlers_from_recipe(short_recipe)
    assert len(tiddlers) == 2, 'tiddler list should be length 2, is %s' % len(tiddlers)

def test_determine_bag_simple():
    """
    Given a tiddler, work out which bag in the recipe it should
    drop into. Usually this won't be used: the client will use
    the default bag.

    This means, which bag does the filter match for.
    """
    bag = control.determine_bag_for_tiddler(recipe, tiddlers[0])
    assert bag.name == bagthree.name, 'bag name should be bagthree, is %s' % bag.name

def test_determine_bag_filtered():
    """
    Work out which bag a tiddler should go to when no bag provided.
    """
    short_recipe = Recipe(name='foobar')
    short_recipe.set_recipe([
        [bagone, ''],
        [bagfour, '[tag[tagone]]']
        ])
    bag = control.determine_bag_for_tiddler(short_recipe, tiddlers[0])
    assert bag.name == bagfour.name, 'bag name should be bagfour, is %s' % bag.name

    short_recipe.set_recipe([
        [bagone, ''],
        [bagfour, '[tag[tagthree]]']
        ])
    bag = control.determine_bag_for_tiddler(short_recipe, tiddlers[0])
    assert bag.name == bagone.name, 'bag name should be bagone, is %s' % bag.name

def test_determine_tiddler_from_recipe():
    """
    Work out what bag a provided tiddler is in, when we have no knowledge of the bag,
    but we do have a recipe.
    """
    short_recipe = Recipe(name='foobar')
    short_recipe.set_recipe([
        [bagone, ''],
        [bagfour, '[tag[tagone]]']
        ])
    bag = control.determine_tiddler_bag_from_recipe(short_recipe, tiddlers[0])
    assert bag.name == bagfour.name, 'bag name should be bagfour, is %s' % bag.name

    short_recipe.set_recipe([
        [bagone, ''],
        [bagfour, '[tag[tagthree]]']
        ])
    bag = control.determine_tiddler_bag_from_recipe(short_recipe, tiddlers[0])
    assert bag.name == bagone.name, 'bag name should be bagone, is %s' % bag.name

    lonely_tiddler = Tiddler('lonely')
    lonely_tiddler.bag = 'lonelybag'

    py.test.raises(NoBagError,
            'bag = control.determine_tiddler_bag_from_recipe(short_recipe, lonely_tiddler)')

def test_determine_bag_fail():

    lonely_recipe = Recipe(name='thing')
    lonely_recipe.set_recipe([
        [bagone, '[tag[hello]]']
        ])

    lonely_tiddler = Tiddler('lonely')
    lonely_tiddler.tags = ['hello']
    bag = control.determine_bag_for_tiddler(lonely_recipe, lonely_tiddler)
    assert bag.name == bagone.name

    lonely_recipe.set_recipe([
        [bagone, '[tag[goodbye]]']
        ])
    py.test.raises(NoBagError,
            'bag = control.determine_bag_for_tiddler(lonely_recipe, lonely_tiddler)')

def test_recipe_policy():
    policy_recipe = Recipe(name='policed')
    # test them all even though only manage is really used
    policy_recipe.policy.manage = ['a']
    policy_recipe.policy.read = ['b']
    policy_recipe.policy.create = ['c']
    policy_recipe.policy.delete = ['d']
    policy_recipe.policy.owner = 'e'

    assert policy_recipe.policy.manage == ['a']
    assert policy_recipe.policy.read == ['b']
    assert policy_recipe.policy.create == ['c']
    assert policy_recipe.policy.delete == ['d']
    assert policy_recipe.policy.owner == 'e'


