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

def _files_in_dir(path):
    return filter(lambda x: not x.startswith('.'), os.listdir(path))


def list_recipes():
    path = os.path.join(store_root, 'recipes')
    recipes = _files_in_dir(path)

    return [Recipe(recipe) for recipe in recipes]

def list_bags():
    path = os.path.join(store_root, 'bags')
    bags = _files_in_dir(path)

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

    _write_policy(bag.policy, bag_path)

def bag_get(bag):
    bag_path = _bag_path(bag.name)
    tiddlers_dir = _tiddlers_dir(bag.name)

    try:
        tiddlers = _files_in_dir(tiddlers_dir)
    except OSError, e:
        raise NoBagError, 'unable to list tiddlers in bag: %s' % e
    for tiddler in tiddlers:
        bag.add_tiddler(Tiddler(title=tiddler))

    bag.policy = _read_policy(bag_path)

    return bag

def _bag_path(bag_name):
    return os.path.join(store_root, 'bags', bag_name)

def _tiddlers_dir(bag_name):
    return os.path.join(_bag_path(bag_name), 'tiddlers')

def _write_policy(policy, bag_path):
    policy_filename = os.path.join(bag_path, 'policy')
    policy_file = codecs.open(policy_filename, 'w', encoding='utf-8')
    policy_file.write(policy)
    policy_file.close()

def _read_policy(bag_path):
    policy_filename = os.path.join(bag_path, 'policy')
    policy_file = codecs.open(policy_filename, encoding='utf-8')
    policy = policy_file.read()
    policy_file.close()
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
        tiddler = serializer.from_string(tiddler_string)
        return tiddler
    except IOError, e:
        raise NoTiddlerError, 'no tiddler for %s: %s' % (tiddler.title, e)
