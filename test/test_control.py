
from tiddlyweb import control
from tiddlyweb.store import NoBagError
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler

import py

from fixtures import tiddlers, bagone, bagtwo, bagthree, bagfour, recipe_list

def setup_module(module):
    module.recipe = Recipe(name='foorecipe')
    module.recipe.set_recipe(recipe_list)

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
        (bagone, ''),
        (bagfour, 'select=tag:tagone')
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
    assert bag.name == bagone.name

def test_determine_bag_filtered():
    """
    Work out which bag a tiddler should go to when no bag provided.
    """
    short_recipe = Recipe(name='foobar')
    short_recipe.set_recipe([
        (bagone, ''),
        (bagfour, 'select=tag:tagone')
        ])
    bag = control.determine_bag_for_tiddler(short_recipe, tiddlers[0])
    assert bag.name == bagfour.name, 'bag name should be bagfour, is %s' % bag.name

    short_recipe.set_recipe([
        (bagone, ''),
        (bagfour, 'select=tag:tagthree')
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
        (bagone, ''),
        (bagfour, 'select=tag:tagone')
        ])
    bag = control.determine_tiddler_bag_from_recipe(short_recipe, tiddlers[0])
    assert bag.name == bagfour.name, 'bag name should be bagfour, is %s' % bag.name

    short_recipe.set_recipe([
        (bagone, ''),
        (bagfour, 'select=tag:tagthree')
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
        (bagone, 'select=tag:hello')
        ])

    lonely_tiddler = Tiddler('lonely')
    lonely_tiddler.tags = ['hello']
    bag = control.determine_bag_for_tiddler(lonely_recipe, lonely_tiddler)
    assert bag.name == bagone.name

    lonely_recipe.set_recipe([
        (bagone, 'select=tag:goodbye')
        ])
    py.test.raises(NoBagError,
            'bag = control.determine_bag_for_tiddler(lonely_recipe, lonely_tiddler)')
