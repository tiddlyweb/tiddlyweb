"""
Data structures required for our testing.
"""

import os
import shutil

from wsgi_intercept import httplib2_intercept
import wsgi_intercept

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

def initialize_app():
    app = load_app()
    def app_fn():
        return app

    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('our_test_domain', 8001, app_fn)

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
container = Tiddlers()
container.add(tiddlers[0])
bagone.tiddlers = container

bagtwo = Bag(name='bagtwo')
container = Tiddlers()
container.add(tiddlers[1])
bagtwo.tiddlers = container

bagthree = Bag(name='bagthree')
container = Tiddlers()
container.add(tiddlers[2])
bagthree.tiddlers = container

bagfour = Bag(name='bagfour')
container = Tiddlers()
for tiddler in tiddlers:
    container.add(tiddler)
bagfour.tiddlers = container

tiddler_collection = Tiddlers()
for tiddler in tiddlers:
    tiddler.bag = u'bagfour'
    tiddler_collection.add(tiddler)

recipe_list = [
        (bagone, u'select=title:TiddlerOne'),
        (bagtwo, u'select=title:TiddlerTwo'),
        (bagthree, u'select=tag:tagone;select=tag:tagthree')
        ]

recipe_list_string = [
        [u'bagone', u'select=title:TiddlerOne'],
        [u'bagtwo', u'select=title:TiddlerTwo'],
        [u'bagthree', u'select=tag:tagone;select=tag:tagthree']
         ]

def _teststore():
    return Store(config['server_store'][0], config['server_store'][1],
            environ={'tiddlyweb.config': config})

def reset_textstore():
    if os.path.exists('store'):
        shutil.rmtree('store')

def muchdata(store):
    for bag_numeral in range(30):
        bag = create_bag(store, bag_numeral)
        for tiddler_numeral in range(10):
            tiddler = create_tiddler(store, bag, tiddler_numeral)

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
