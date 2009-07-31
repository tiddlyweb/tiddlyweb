
"""
Test a recipe to confirm it does all its recipe
things.
"""

import py.test

from tiddlyweb.model.recipe import Recipe

recipe_list = [
        [u'bagone', u'select=title:TiddlerOne'],
        [u'bagtwo', u'select=title:TiddlerTwo'],
        [u'bagthree', u'select=tag:tagone;select=tag:tagthree']
         ]

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
