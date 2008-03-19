"""
Simple functios for storing bags as textfile
on the filesystem.
"""

# get from config!
store_root = 'store'

import os
import codecs

from tiddlyweb.bag import Bag
from tiddlyweb.recipe import Recipe
from tiddlyweb.tiddler import Tiddler
from tiddlyweb.serializer import Serializer
from tiddlyweb.store import NoBagError, NoRecipeError, NoTiddlerError

def list_recipes():
    path = os.path.join(store_root, 'recipes')
    recipes = os.listdir(path)

    return [Recipe(recipe) for recipe in recipes]

def list_bags():
    path = os.path.join(store_root, 'bags')
    bags = os.listdir(path)

    return [Bag(bag) for bag in bags]

def recipe_put(recipe):
    recipe_path = _recipe_path(recipe)

    recipe_file = codecs.open(recipe_path, 'w', encoding='utf-8')

    serializer = Serializer('text')
    serializer.object = recipe

    recipe_file.write(serializer.to_string())

    recipe_file.close()

def recipe_get(recipe):
    recipe_path = _recipe_path(recipe)

    try:
        recipe_file = codecs.open(recipe_path, encoding='utf-8')
        serializer = Serializer('text')
        serializer.object = recipe
        recipe_string = recipe_file.read()
        recipe_file.close()
    except IOError, e:
        raise NoRecipeError, 'unable to get recipe %s: %s' % (recipe.name, e)

    return serializer.from_string(recipe_string)

def _recipe_path(recipe):
    return os.path.join(store_root, 'recipes', recipe.name)

def bag_put(bag):

    bag_path = _bag_path(bag.name)
    tiddlers_dir = _tiddlers_dir(bag.name)

    if not os.path.exists(bag_path):
        os.mkdir(bag_path)

    if not os.path.exists(tiddlers_dir):
        os.mkdir(tiddlers_dir)

    _write_security_policy(bag.policy, bag_path)

def bag_get(bag):
    bag_path = _bag_path(bag.name)
    tiddlers_dir = _tiddlers_dir(bag.name)

    try:
        tiddlers = os.listdir(tiddlers_dir)
    except OSError, e:
        raise NoBagError, 'unable to list tiddlers in bag: %s' % e
    for tiddler in tiddlers:
        bag.add_tiddler(Tiddler(title=tiddler))

    bag.policy = _read_security_policy(bag_path)

    return bag

def _bag_path(bag_name):
    return os.path.join(store_root, 'bags', bag_name)

def _tiddlers_dir(bag_name):
    return os.path.join(_bag_path(bag_name), 'tiddlers')

def _write_security_policy(policy, bag_path):
    security_filename = os.path.join(bag_path, 'security_policy')
    security_file = codecs.open(security_filename, 'w', encoding='utf-8')
    security_file.write(policy)
    security_file.close()

def _read_security_policy(bag_path):
    security_filename = os.path.join(bag_path, 'security_policy')
    security_file = codecs.open(security_filename, encoding='utf-8')
    policy = security_file.read()
    security_file.close()
    return policy

def tiddler_put(tiddler):
    """
    Write a tiddler into the store. We only write if
    the bag already exists. Bag creation is a 
    separate action from writing to a bag.
    """

    # should be get a Bag or a name here?
    bag_name = tiddler.bag

    store_dir = _tiddlers_dir(bag_name)

    if not os.path.exists(store_dir):
        raise NoBagError, "%s does not exist" % store_dir

    tiddler_filename = os.path.join(store_dir, tiddler.title)
    tiddler_file = codecs.open(tiddler_filename, 'w', encoding='utf-8')

    serializer = Serializer('text')
    serializer.object = tiddler

    tiddler_file.write(serializer.to_string())

    tiddler_file.close()

def tiddler_get(tiddler):
    """
    Get a tiddler as string from a bag and deserialize it into 
    object.
    """

    bag_name = tiddler.bag

    store_dir = _tiddlers_dir(bag_name)

    try:
        tiddler_filename = os.path.join(store_dir, tiddler.title)
        tiddler_file = codecs.open(tiddler_filename, encoding='utf-8')
        serializer = Serializer('text')
        serializer.object = tiddler
        tiddler_string = tiddler_file.read()
        tiddler_file.close()
        return serializer.from_string(tiddler_string)
    except IOError, e:
        raise NoTiddlerError, 'no tiddler for %s: %s' % (tiddler.title, e)
