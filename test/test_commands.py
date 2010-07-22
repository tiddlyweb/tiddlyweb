"""
Test the manager a little bit.
"""

import os
import sys
from StringIO import StringIO

from fixtures import reset_textstore

from tiddlyweb import __version__
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
    module.savedin = sys.stdin
    sys.exit = boring_exit
    module.store = Store(config['server_store'][0],
            config['server_store'][1],
            environ={'tiddlyweb.config': config})

class InternalExit(Exception):
    pass

def boring_exit(value):
    raise InternalExit()

def teardown_module(module):
    sys.stdin = module.savedin


def test_adduser():
    handle(['', u'adduser', u'cdent', u'crunk'])
    the_user = User('cdent')
    the_user = store.get(the_user)
    assert the_user.check_password('crunk')

def test_adduser_with_roles():
    handle(['', u'adduser', u'cdent', u'crunk', u'cow', u'monkey'])
    the_user = User('cdent')
    the_user = store.get(the_user)
    assert the_user.check_password('crunk')
    assert 'cow' in the_user.list_roles()
    assert 'monkey' in the_user.list_roles()

def test_addrole():
    handle(['', u'addrole', u'cdent', u'pig'])
    the_user = User('cdent')
    the_user = store.get(the_user)
    assert 'cow' in the_user.list_roles()

def test_userpass():
    handle(['', u'userpass', u'cdent', u'drunk'])
    the_user = User('cdent')
    the_user = store.get(the_user)
    assert the_user.check_password('drunk')

def test_bag():
    set_stdin(BAG_STRING)
    handle(['', u'bag', u'bag1'])

    the_bag = Bag('bag1')
    the_bag = store.get(the_bag)

    assert the_bag.name == 'bag1'
    assert the_bag.desc == 'hello'

def test_recipe():
    set_stdin(RECIPE_STRING)
    handle(['', u'recipe', u'recipe1'])

    the_recipe = Recipe('recipe1')
    the_recipe = store.get(the_recipe)

    assert the_recipe.name == 'recipe1'
    assert u'bag1' in the_recipe.get_recipe()[0]
    assert u'bag2' in the_recipe.get_recipe()[1]

def test_tiddler():
    set_stdin(TIDDLER_STRING)
    handle(['', u'tiddler', u'bag1', u'tiddler1'])

    the_tiddler = Tiddler('tiddler1', 'bag1')
    the_tiddler = store.get(the_tiddler)

    assert the_tiddler.title == 'tiddler1'
    assert the_tiddler.bag == u'bag1'
    assert the_tiddler.modifier == 'cdent'

def test_info(capsys):
    handle(['', 'info'])
    results, err = capsys.readouterr()
    assert 'current store is' in results
    assert __version__ in results

def test_server(capsys):
    import tiddlyweb.web.serve
    def start_cherrypy(config):
        print 'host is %s' % config['server_host']['host']
    tiddlyweb.web.serve.start_cherrypy = start_cherrypy
    handle(['', 'server'])
    results, err = capsys.readouterr()
    assert 'host is our_test_domain' in results

    handle(['', 'server', '192.168.1.1', '8001'])
    results, err = capsys.readouterr()
    assert 'host is 192.168.1.1' in results
    config['server_host']['host'] = 'our_test_domain'

def test_lusers(capsys):
    handle(['', 'lusers'])
    results, err = capsys.readouterr()
    # cdent user with role monkey was created above
    assert 'cdent' in results
    assert 'monkey' in results

def test_lbags(capsys):
    handle(['', u'lbags'])
    results, err = capsys.readouterr()
    assert 'Name: bag1' in results

def test_lrecipes(capsys):
    handle(['', u'lrecipes'])
    results, err = capsys.readouterr()
    assert 'recipe1 ' in results

def test_ltiddlers(capsys):
    handle(['', u'ltiddlers'])
    results, err = capsys.readouterr()
    assert 'bag1' in results
    assert '\ttiddler1' in results
    handle(['', 'ltiddlers', 'bag1'])
    results, err = capsys.readouterr()
    assert 'bag1' in results
    assert '\ttiddler1' in results

def set_stdin(content):
    f = StringIO(content)
    sys.stdin = f
