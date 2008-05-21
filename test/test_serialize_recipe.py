
"""
Test turning a recipe into other forms.
"""

import sys
sys.path.append('.')

from tiddlyweb.recipe import Recipe
from tiddlyweb.serializer import Serializer

from fixtures import recipe_list

expected_string = """/bags/bagone/tiddlers?TiddlerOne
/bags/bagtwo/tiddlers?TiddlerTwo
/bags/bagthree/tiddlers?%5Btag%5Btagone%5D%5D%20%5Btag%5Btagthree%5D%5D"""

expected_html_string = """<ul>
<li><a href="/bags/bagone/tiddlers?TiddlerOne">bag: bagone filter:TiddlerOne</a></li>
<li><a href="/bags/bagtwo/tiddlers?TiddlerTwo">bag: bagtwo filter:TiddlerTwo</a></li>
<li><a href="/bags/bagthree/tiddlers?%5Btag%5Btagone%5D%5D%20%5Btag%5Btagthree%5D%5D">bag: bagthree filter:[tag[tagone]] [tag[tagthree]]</a></li>
</ul>"""

def setup_module(module):
    module.recipe = Recipe(name='testrecipe')
    module.recipe.set_recipe(recipe_list)

def test_generated_text():
    serializer = Serializer('text')
    serializer.object = recipe
    string = serializer.to_string()

    assert string == expected_string, \
            'serialized recipe looks like we expect. should be %s, got %s' \
            % (expected_string, string)

    assert '%s' % serializer == expected_string, \
            'serializer goes to string as expected_string'

def test_generated_html():
    serializer = Serializer('html')
    serializer.object = recipe
    string = serializer.to_string()

    assert string == expected_html_string
    assert '%s' % serializer == expected_html_string

def test_generated_wiki():
    serializer = Serializer('wiki')
    serializer.object = recipe
    string = serializer.to_string()

    assert string.startswith('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'), 'looks like we got an empty.html doc'
    assert 'c tiddler one' in string
    assert '<div title="TiddlerOne" server.page.revision="None" modifier="AuthorOne"' in string

def test_simple_recipe():
    recipe = Recipe('other')
    recipe.set_recipe([['bagbuzz', '']])
    serializer = Serializer('text')
    serializer.object = recipe
    string = serializer.to_string()

    new_recipe = Recipe('other')
    serializer.object = new_recipe
    serializer.from_string(string)

    assert recipe == new_recipe, 'recipe and new_recipe have equality'

    recipe = Recipe('other')
    recipe.set_recipe([['bagboom', '']])
    assert recipe != new_recipe, 'modified recipe not equal new_recipe'

def test_json_recipe():
    """
    JSON serializer roundtrips.
    """
    recipe = Recipe('other')
    recipe.set_recipe([['bagbuzz', '']])
    serializer = Serializer('json')
    serializer.object = recipe
    string = serializer.to_string()

    other_recipe = Recipe('other')
    serializer.object = other_recipe
    serializer.from_string(string)

    assert recipe == other_recipe

    serializer.object = other_recipe
    other_string = serializer.to_string()

    assert string == other_string
