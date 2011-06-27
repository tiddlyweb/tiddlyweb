
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
    assert len(recipe.get_recipe()) == 3

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

def test_get_recipe_list_templated_bag():
    recipe = Recipe('tr')
    recipe.set_recipe([
        ('{{ user }}', '')
        ])
    list = recipe.get_recipe({'user': 'testuser'})
    assert list[0][0] == 'testuser'


def test_get_recipe_list_templated_filter():
    recipe = Recipe('tr')
    recipe.set_recipe([
        ('system', 'modifier={{ user }}')
        ])
    list = recipe.get_recipe({'user': 'testuser'})
    assert list[0][1] == 'modifier=testuser'

def test_get_recipe_list_templated_filter2():
    recipe = Recipe('tr')
    recipe.set_recipe([
        ('system', 'modifier={{ user }};creator={{ user }}')
        ])
    list = recipe.get_recipe({'user': 'testuser'})
    assert list[0][1] == 'modifier=testuser;creator=testuser'

def test_get_recipe_list_templated_bag_filter():
    recipe = Recipe('tr')
    recipe.set_recipe([
        ('{{ bagname }}', 'modifier={{ user }}')
        ])
    list = recipe.get_recipe({'user': 'testuser', 'bagname': 'foobar'})
    assert list[0][1] == 'modifier=testuser'
    assert list[0][0] == 'foobar'

def test_get_recipe_list_templated_bag_filter_defaulted_bag():
    recipe = Recipe('tr')
    recipe.set_recipe([
        ('{{ bagname:common }}', 'modifier={{ user }}')
        ])
    list = recipe.get_recipe({'user': 'testuser'})
    assert list[0][1] == 'modifier=testuser'
    assert list[0][0] == 'common'


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
