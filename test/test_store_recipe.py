"""
Exploratory testing for storing recipes.

"""

import os
import sys
import shutil
sys.path.append('.')

from fixtures import textstore, reset_textstore, recipe_list_string
from tiddlyweb.recipe import Recipe
from tiddlyweb.store import Store

expected_stored_filename = os.path.join(textstore.recipe_store, 'testrecipe')

expected_stored_content = """/bags/bagone/tiddlers?TiddlerOne
/bags/bagtwo/tiddlers?TiddlerTwo
/bags/bagthree/tiddlers?%5Btag%5Btagone%5D%5D%20%5Btag%5Btagthree%5D%5D"""

def setup_module(module):
    """
    Need to clean up the store here.
    """
    reset_textstore()

def test_recipe_put():
    """
    put a recipe to disk and make sure it is there.
    """

    recipe = Recipe('testrecipe')
    recipe.set_recipe(recipe_list_string)
    store = Store('text')
    store.put(recipe)

    assert os.path.exists(expected_stored_filename), \
            'path %s should be created' \
            % expected_stored_filename

    f = file(expected_stored_filename)
    content = f.read()

    assert content == expected_stored_content, \
            'stored content should be %s, got %s' \
            % (expected_stored_content, content)

def test_recipe_get():
    """
    get a recipe from disk and confirm it has proper form.
    """

    stored_recipe = Recipe('testrecipe')
    store = Store('text')
    store.get(stored_recipe)

    assert stored_recipe == recipe_list_string
