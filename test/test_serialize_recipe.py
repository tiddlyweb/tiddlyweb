
"""
Test turning a recipe into other forms.
"""

import sys
sys.path.append('.')
from tiddlyweb.recipe import Recipe
from tiddlyweb.serializer import Serializer

from fixtures import recipe_list

expected_string = """/bags/bagone?TiddlerOne
/bags/bagtwo?TiddlerTwo
/bags/bagthree?%5Btag%5Btagone%5D%5D%20%5Btag%5Btagthree%5D%5D"""

def setup_module(module):
    pass

def test_generated_string():

    recipe = Recipe(name='testrecipe')
    recipe.set_recipe(recipe_list)

    serializer = Serializer(recipe, 'text')
    string = serializer.to_string()

    assert string == expected_string, \
            'serialized recipe looks like we expect. should be %s, got %s' \
            % (expected_string, string)

    assert '%s' % serializer == expected_string, \
            'serializer goes to string as expected_string'
