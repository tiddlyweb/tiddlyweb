"""
Get coverage on specialbag handling.
"""

from tiddlyweb.config import config
from tiddlyweb.control import get_tiddlers_from_recipe
from tiddlyweb.store import Store
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler


def get_x_tiddlers(environ, name):
    for title in ['alpha', 'beta', 'gamma']:
        yield Tiddler(title, name)


def get_x_tiddler(environ, tiddler):
    tiddler.text = tiddler.title
    return tiddler


def spector(environ, bagname):
    """
    Simple special bag detector.
    """
    def curry(environ, func):
        def actor(bag):
            return func(environ, bag)
        return actor

    if bagname.startswith('X'):
        return (curry(environ, get_x_tiddlers),
                curry(environ, get_x_tiddler))
    return None


def setup_module(module):
    config['special_bag_detectors'] = [spector]
    module.environ = {'tiddlyweb.config': config}
    module.store = Store(config['server_store'][0], config['server_store'][1],
            environ=module.environ)


def test_two_bags():
    bag_normal = Bag('normal')
    store.put(bag_normal)
    tiddler_normal = Tiddler('thing', 'normal')
    tiddler_normal.text = 'hi'
    store.put(tiddler_normal)

    tiddlers = store.list_bag_tiddlers(bag_normal)
    assert 'thing' in [tiddler.title for tiddler in tiddlers]

    bag_special = Bag('Xnine')
    tiddlers = store.list_bag_tiddlers(bag_special)
    assert 'alpha' in [tiddler.title for tiddler in tiddlers]
    tiddler = Tiddler('alpha', 'Xnine')
    tiddler = store.get(tiddler)
    assert tiddler.text == 'alpha'

def test_recipe_with_special():
    recipe = Recipe('special')
    recipe.set_recipe([
        ('normal', ''),
        ('Xnine', '')])
    recipe.store = store

    tiddlers = list(get_tiddlers_from_recipe(recipe, environ))

    assert len(tiddlers) == 4
    assert 'thing' in [tiddler.title for tiddler in tiddlers]
    assert 'alpha' in [tiddler.title for tiddler in tiddlers]
    assert 'beta' in [tiddler.title for tiddler in tiddlers]
    assert 'gamma' in [tiddler.title for tiddler in tiddlers]

    # roundtrip the recipes with a special
    store.put(recipe)
    recipe2 = store.get(Recipe('special'))

    assert recipe.get_recipe() == recipe2.get_recipe()

