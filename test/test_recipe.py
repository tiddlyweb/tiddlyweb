
"""
Test a recipe to confirm it does all its recipe
things.
"""

import sys
sys.path.append('.')
from tiddlyweb.recipe import Recipe

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

    tiddlers = recipe.get_tiddlers()
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
    tiddlers = short_recipe.get_tiddlers()
    assert len(tiddlers) == 2, 'tiddler list should be length 2, is %s' % len(tiddlers)

def test_determine_bag_simple():
    """
    Given a tiddler, work out which bag in the recipe it should
    drop into. Usually this won't be used: the client will use
    the default bag.

    This means, which bag does the filter match for.
    """
    bag = recipe.determine_bag(tiddlers[0])
    assert bag.name == bagthree.name, 'bag name should be bagthree, is %s' % bag.name

def test_determine_bag_filtered():
    """
    Work out which bag a tiddler should go to.
    """
    short_recipe = Recipe(name='foobar')
    short_recipe.set_recipe([
        [bagone, ''],
        [bagfour, '[tag[tagone]]']
        ])
    bag = short_recipe.determine_bag(tiddlers[0])
    assert bag.name == bagfour.name, 'bag name should be bagfour, is %s' % bag.name

    short_recipe.set_recipe([
        [bagone, ''],
        [bagfour, '[tag[tagthree]]']
        ])
    bag = short_recipe.determine_bag(tiddlers[0])
    assert bag.name == bagone.name, 'bag name should be bagone, is %s' % bag.name
