"""
Data structures required for our testing.
"""

import sys
sys.path.append('.')

import os
import shutil

from tiddlyweb.bag import Bag
from tiddlyweb.tiddler import Tiddler
from tiddlyweb.recipe import Recipe

tiddlers = [
        Tiddler(
            title='TiddlerOne',
            modifier='AuthorOne',
            text='c tiddler one content',
            tags=['tagone', 'tagtwo']
        ),
        Tiddler(
            title='TiddlerTwo',
            modifier='AuthorTwo',
            text='b tiddler two content',
        ),
        Tiddler(
            title='TiddlerThree',
            modifier='AuthorThree',
            text='a tiddler three content',
            tags=['tagone', 'tagthree']
        )
]

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
         [bagone, 'TiddlerOne'],
         [bagtwo, 'TiddlerTwo'],
         [bagthree, '[tag[tagone]] [tag[tagthree]]']
         ]

recipe_list_string = [
         ['bagone', 'TiddlerOne'],
         ['bagtwo', 'TiddlerTwo'],
         ['bagthree', '[tag[tagone]] [tag[tagthree]]']
         ]

class textstore:

    store_dirname = 'store'
    bag_store = os.path.join(store_dirname, 'bags')
    recipe_store = os.path.join(store_dirname, 'recipes')

def reset_textstore():
    if os.path.exists(textstore.store_dirname):
        shutil.rmtree(textstore.store_dirname)
    os.makedirs(textstore.bag_store)
    os.makedirs(textstore.recipe_store)

def muchdata(store):
    for bag_numeral in range(30):
        bag = create_bag(store, bag_numeral)
        for tiddler_numeral in range(10):
            tiddler = create_tiddler(store, bag, tiddler_numeral)

    recipe = Recipe('long')

    recipe_list = [['bag1', '']]
    for numeral in range(0, 30, 2):
        bag_name = 'bag%s' % numeral
        filter_string = 'tiddler%s' % (numeral % 10)
        if not (numeral % 10) % 3:
            filter_string = filter_string + ' [tag[tag three]]'
        recipe_list.append([bag_name, filter_string])
    recipe.set_recipe(recipe_list)

    store.put(recipe)


def create_tiddler(store, bag, numeral):
    tiddler = Tiddler('tiddler%s' % numeral)
    tiddler.bag = bag.name
    tiddler.text = 'i am tiddler %s' % numeral
    tags = ['basic tag']
    if not numeral % 2:
        tags.append('tagtwo')
    if not numeral % 3:
        tags.append('tagthree')
    if not numeral % 4:
        tags.append('tagfour')
    tiddler.tags = tags
    store.put(tiddler)

def create_bag(store, numeral):
    bag = Bag('bag%s' % numeral)
    store.put(bag)
    return bag


