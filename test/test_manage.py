"""
Test the manager a little bit.
"""

import os
import sys
from StringIO import StringIO

from fixtures import reset_textstore

from tiddlyweb.config import config
from tiddlyweb.manage import handle
from tiddlyweb.store import Store
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.user import User

BAG_STRING = """
{"desc": "hello", "policy": {}}
"""

RECIPE_STRING = """/bags/bag1/tiddlers
/bags/bag2/tiddlers
"""

TIDDLER_STRING = """modifier: cdent

Hello!
"""


def setup_module(module):
    reset_textstore()
    module.savedout = sys.stdout
    module.savedin = sys.stdin
    module.output = StringIO()
    sys.stdout = output
    module.store = Store(config['server_store'][0], environ={'tiddlyweb.config': config})


def teardown_module(module):
    content = module.output.getvalue()
    sys.stdout = module.savedout
    sys.stdin = module.savedin


def test_adduser():
    handle(['', 'adduser', 'cdent', 'crunk'])
    the_user = User('cdent')
    the_user = store.get(the_user)
    assert the_user.check_password('crunk')


def test_bag():
    set_stdin(BAG_STRING)
    handle(['', 'bag', 'bag1'])

    the_bag = Bag('bag1')
    the_bag = store.get(the_bag)

    assert the_bag.name == 'bag1'
    assert the_bag.desc == 'hello'


def test_recipe():
    set_stdin(RECIPE_STRING)
    handle(['', 'recipe', 'recipe1'])

    the_recipe = Recipe('recipe1')
    the_recipe = store.get(the_recipe)

    assert the_recipe.name == 'recipe1'
    assert u'bag1' in the_recipe.get_recipe()[0]
    assert u'bag2' in the_recipe.get_recipe()[1]


def test_tiddler():
    set_stdin(TIDDLER_STRING)
    handle(['', 'tiddler', 'tiddler1', 'bag1'])

    the_tiddler = Tiddler('tiddler1', 'bag1')
    the_tiddler = store.get(the_tiddler)

    assert the_tiddler.title == 'tiddler1'
    assert the_tiddler.bag == 'bag1'
    assert the_tiddler.modifier == 'cdent'


def set_stdin(content):
    f = StringIO(content)
    sys.stdin = f

