from tiddlyweb import control
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.config import config

from tiddlywebplugins.utils import get_store

from fixtures import reset_textstore, _teststore

import shutil

def setup_module(module):
    reset_textstore()
    module.store = _teststore()


def test_in_a_recipe():
    bag = Bag('hi')
    store.put(bag)
    tiddler = Tiddler('thing1', 'hi')
    tiddler.tags = ['research']
    store.put(tiddler)
    tiddler = Tiddler('thing2', 'hi')
    store.put(tiddler)

    recipe1 = Recipe('oi')
    recipe1.set_recipe([('hi', 'select=tag:research')])
    recipe1.store = store
    recipe2 = Recipe('boi')
    recipe2.set_recipe([('hi', '')])
    recipe2.store = store
    environ = {'tiddlyweb.store': store}
    tiddlers = list(control.get_tiddlers_from_recipe(recipe1, environ))
    assert len(tiddlers) == 1
    tiddlers = list(control.get_tiddlers_from_recipe(recipe2, environ))
    assert len(tiddlers) == 2
