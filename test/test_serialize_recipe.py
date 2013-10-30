
"""
Test turning a recipe into other forms.
"""

import pytest
import sys
py_version = sys.version_info[0]

from tiddlyweb.model.recipe import Recipe
from tiddlyweb.serializer import Serializer


recipe_list = [
        ('bagone', u'select=title:TiddlerOne'),
        ('bagtwo', u'select=title:TiddlerTwo'),
        ('bagthree', u'select=tag:tagone;select=tag:tagthree')
]

expected_string = """desc: 
policy: {"read": [], "create": [], "manage": [], "accept": [], "write": [], "owner": null, "delete": []}

/bags/bagone/tiddlers?select=title:TiddlerOne
/bags/bagtwo/tiddlers?select=title:TiddlerTwo
/bags/bagthree/tiddlers?select=tag:tagone;select=tag:tagthree"""

no_desc = """/bags/bagone/tiddlers?select=title:TiddlerOne
/bags/bagtwo/tiddlers?select=title:TiddlerTwo
/bags/bagthree/tiddlers?select=tag:tagone;select=tag:tagthree"""

expected_html_string = """<div id="recipedesc" class="description">Courage of Bags</div>
<ul id="recipe" class="listing">
<li><a href="/bags/bagone/tiddlers?select=title:TiddlerOne">bag: bagone filter:select=title:TiddlerOne</a></li>
<li><a href="/bags/bagtwo/tiddlers?select=title:TiddlerTwo">bag: bagtwo filter:select=title:TiddlerTwo</a></li>
<li><a href="/bags/bagthree/tiddlers?select=tag:tagone;select=tag:tagthree">bag: bagthree filter:select=tag:tagone;select=tag:tagthree</a></li>
</ul>"""


def setup_module(module):
    module.recipe = Recipe(name='testrecipe')
    module.recipe.set_recipe(recipe_list)


@pytest.mark.skipif(py_version > 2, reason='python 2 required')
def test_generated_text():
    serializer = Serializer('text')
    serializer.object = recipe
    string = serializer.to_string()

    assert string == expected_string
    assert '%s' % serializer == expected_string


def test_simple_recipe():
    recipe = Recipe('other')
    recipe.set_recipe([('bagbuzz', '')])
    recipe.policy.manage = ['a']
    recipe.policy.read = ['b']
    recipe.policy.create = ['c']
    recipe.policy.delete = ['d']
    recipe.policy.owner = 'e'
    serializer = Serializer('text')
    serializer.object = recipe
    string = serializer.to_string()

    new_recipe = Recipe('other')
    serializer.object = new_recipe
    serializer.from_string(string)

    assert recipe.get_recipe() == new_recipe.get_recipe()

    recipe = Recipe('other')
    recipe.set_recipe([('bagboom', '')])
    assert recipe != new_recipe


def test_json_recipe():
    """
    JSON serializer roundtrips.
    """
    recipe = Recipe('other')
    recipe.set_recipe([('bagbuzz', '')])
    recipe.policy.manage = ['a']
    recipe.policy.read = ['b']
    recipe.policy.create = ['c']
    recipe.policy.delete = ['d']
    recipe.policy.owner = 'e'
    serializer = Serializer('json')
    serializer.object = recipe
    string = serializer.to_string()

    other_recipe = Recipe('other')
    serializer.object = other_recipe
    serializer.from_string(string)

    serializer.object = other_recipe
    other_string = serializer.to_string()

    assert string == other_string


@pytest.mark.skipif(py_version > 2, reason='python 2 required')
def test_old_text():
    """
    Send in text without a description
    and make sure we are able to accept it.
    """
    recipe = Recipe('other')
    serializer = Serializer('text')
    serializer.object = recipe
    serializer.from_string(no_desc)

    output = serializer.to_string()

    assert output == expected_string


def test_generated_html():
    serializer = Serializer('html')
    recipe.desc = 'Courage of Bags'
    serializer.object = recipe
    string = serializer.to_string()

    assert expected_html_string in string
    assert expected_html_string in '%s' % serializer


def test_text_list():
    serializer = Serializer('text')
    recipes = [Recipe('recipe' + str(name)) for name in range(2)]
    string = ''.join(serializer.list_recipes(recipes))

    assert string == 'recipe0\nrecipe1\n'


def test_html_list():
    serializer = Serializer('html')
    recipes = [Recipe('recipe' + str(name)) for name in range(2)]
    string = ''.join(serializer.list_recipes(recipes))

    assert 'href="recipes/recipe0' in string
    assert 'href="recipes/recipe1' in string
