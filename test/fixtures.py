"""
Data structures required for our testing.
"""

import os
import shutil

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
bagone.add_tiddler(tiddlers[0])
bagtwo = Bag(name='bagtwo')
bagtwo.add_tiddler(tiddlers[1])
bagthree = Bag(name='bagthree')
bagthree.add_tiddler(tiddlers[2])
bagfour = Bag(name='bagfour')
bagfour.add_tiddler(tiddlers[0])
bagfour.add_tiddler(tiddlers[1])
bagfour.add_tiddler(tiddlers[2])

recipe_list = [
        (bagone, u'select=title:TiddlerOne'),
        (bagtwo, u'select=title:TiddlerTwo'),
        (bagthree, u'select=tag:tagone;select=tag:tagthree')
        ]

recipe_list_string = [
        (u'bagone', u'select=title:TiddlerOne'),
        (u'bagtwo', u'select=title:TiddlerTwo'),
        (u'bagthree', u'select=tag:tagone;select=tag:tagthree')
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
