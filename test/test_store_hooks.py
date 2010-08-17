
import sys
from StringIO import StringIO
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.config import config
from tiddlywebplugins.utils import get_store

from tiddlyweb.store import HOOKS

OUTPUT = ''

def recipe_put_hook(store, recipe):
    global OUTPUT
    OUTPUT += 'recipe put hook ahoy! %s' % recipe.name

def recipe_get_hook(store, recipe):
    global OUTPUT
    OUTPUT += 'recipe get hook ahoy! %s' % recipe.name

def setup_module(module):
    module.store = get_store(config)
    HOOKS['recipe']['put'].append(recipe_put_hook)
    HOOKS['recipe']['get'].append(recipe_get_hook)


def teardown_module(module):
    HOOKS['recipe']['put'].remove(recipe_put_hook)
    HOOKS['recipe']['get'].remove(recipe_get_hook)


def test_put_recipe():
    global OUTPUT
    assert OUTPUT == ''
    recipe = Recipe('keen')
    store.put(recipe)
    store.get(recipe)
    assert 'recipe put hook ahoy' in OUTPUT
    assert 'recipe get hook ahoy' in OUTPUT
