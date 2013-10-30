"""
Data structures required for our testing.
"""

import os
import shutil

from wsgi_intercept import httplib2_intercept
import wsgi_intercept

import httplib2

from tiddlyweb.web.serve import load_app
from tiddlyweb.model.collections import Tiddlers
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.config import config
from tiddlyweb.store import Store

config['server_host'] = {
        'scheme': 'http',
        'host': 'our_test_domain',
        'port': '8001',
        }

TiddlerOne = Tiddler('TiddlerOne')
TiddlerOne.modifier = 'AuthorOne'
TiddlerOne.text = u'c tiddler one content'
TiddlerOne.tags = ['tagone', 'tagtwo']

TiddlerTwo = Tiddler('TiddlerTwo')
TiddlerTwo.modifier = u'AuthorTwo'
TiddlerTwo.text = u'b tiddler two content'

TiddlerThree = Tiddler('TiddlerThree')
TiddlerThree.modifier = u'AuthorThree'
TiddlerThree.text = u'a tiddler three content'
TiddlerThree.tags = [u'tagone', u'tagthree']

tiddlers = [TiddlerOne, TiddlerTwo, TiddlerThree]

bagone = Bag(name='bagone')
bagtwo = Bag(name='bagtwo')
bagthree = Bag(name='bagthree')
bagfour = Bag(name='bagfour')

tiddler_collection = Tiddlers()
for tiddler in tiddlers:
    tiddler.bag = u'bagfour'
    tiddler_collection.add(tiddler)


def initialize_app():
    app = load_app()

    def app_fn():
        return app

    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('our_test_domain', 8001, app_fn)


def get_store(config):
    return Store(config['server_store'][0], config['server_store'][1],
            {'tiddlyweb.config': config})


def _teststore():
    """
    Different from the above because it is using config loaded in this
    module. Kept for backwards awareness.
    """
    return Store(config['server_store'][0], config['server_store'][1],
            environ={'tiddlyweb.config': config})


def reset_textstore():
    if os.path.exists('store'):
        shutil.rmtree('store')


def muchdata(store):
    for bag_numeral in range(30):
        bag = create_bag(store, bag_numeral)
        for tiddler_numeral in range(10):
            create_tiddler(store, bag, tiddler_numeral)

    recipe = Recipe('long')

    recipe_list = [(u'bag1', '')]
    for numeral in range(0, 30, 2):
        bag_name = u'bag%s' % numeral
        filter_string = u'select=title:tiddler%s' % (numeral % 10)
        if not (numeral % 10) % 3:
            filter_string = filter_string + u';select=tag:tag three'
        recipe_list.append([bag_name, filter_string])
    recipe.set_recipe(recipe_list)

    store.put(recipe)


def create_tiddler(store, bag, numeral):
    tiddler = Tiddler('tiddler%s' % numeral)
    tiddler.bag = bag.name
    tiddler.text = u'i am tiddler %s' % numeral
    tags = [u'basic tag']
    if not numeral % 2:
        tags.append(u'tagtwo')
    if not numeral % 3:
        tags.append(u'tagthree')
    if not numeral % 4:
        tags.append(u'tagfour')
    tiddler.tags = tags
    if tiddler.title == 'tiddler8':
        tiddler.modified = '200805230303'
    store.put(tiddler)


def create_bag(store, numeral):
    bag = Bag('bag%s' % numeral)
    store.put(bag)
    return bag


def get_http():
    """
    Get a httplib2 object, patched to provide a requestU method
    which returns decoded content.
    """
    def requestU(*args, **kwargs):
        self = args[0]
        args = args[1:]
        response, content = self.request(*args, **kwargs)
        return response, content.decode('utf-8')

    http = httplib2.Http()
    http.__class__.requestU = requestU
    return http
