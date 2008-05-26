"""
Simple functios for storing bags as textfile
on the filesystem.
"""

# get from config!
store_root = 'store'

import os
import codecs
import time
import simplejson

from tiddlyweb.bag import Bag, Policy
from tiddlyweb.recipe import Recipe
from tiddlyweb.tiddler import Tiddler
from tiddlyweb.serializer import Serializer
from tiddlyweb.store import NoBagError, NoRecipeError, NoTiddlerError, StoreLockError

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

def recipe_put(recipe):
    recipe_path = _recipe_path(recipe)

    recipe_file = codecs.open(recipe_path, 'w', encoding='utf-8')

    serializer = Serializer('text')
    serializer.object = recipe

    recipe_file.write(serializer.to_string())

    recipe_file.close()

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

def bag_put(bag):
    bag_path = _bag_path(bag.name)
    tiddlers_dir = _tiddlers_dir(bag.name)

    if not os.path.exists(bag_path):
        os.mkdir(bag_path)

    if not os.path.exists(tiddlers_dir):
        os.mkdir(tiddlers_dir)

    _write_policy(bag.policy, bag_path)

def tiddler_get(tiddler):
    """
    Get a tiddler as string from a bag and deserialize it into 
    object.
    """
    try:
        # read in the desired tiddler
        tiddler = _read_tiddler_revision(tiddler)
        # now make another tiddler to get created time 
        # base_tiddler is the head of the revision stack
        base_tiddler = Tiddler(tiddler.title)
        base_tiddler.bag = tiddler.bag
        base_tiddler = _read_tiddler_revision(base_tiddler, index=-1)
        # set created on new tiddler from modified on base_tiddler (might be the same)
        tiddler.created = base_tiddler.modified
        return tiddler
    except IOError, e:
        raise NoTiddlerError, 'no tiddler for %s: %s' % (tiddler.title, e)

def tiddler_put(tiddler):
    """
    Write a tiddler into the store. We only write if
    the bag already exists. Bag creation is a 
    separate action from writing to a bag.

    XXX: This should be in a try with a finally?
    """

    tiddler_base_filename = _tiddler_base_filename(tiddler)
    if not os.path.exists(tiddler_base_filename):
        os.mkdir(tiddler_base_filename)
    locked = 0
    lock_attempts = 0
    while (not locked):
        try:
            lock_attempts = lock_attempts + 1
            write_lock(tiddler_base_filename)
            locked = 1
        except StoreLockError, e:
            if lock_attempts > 4:
                raise StoreLockError, e
            time.sleep(.1)

    tiddler_filename = os.path.join(tiddler_base_filename, '%s' % (_tiddler_revision_filename(tiddler) + 1))
    tiddler_file = codecs.open(tiddler_filename, 'w', encoding='utf-8')

    serializer = Serializer('text')
    serializer.object = tiddler

    tiddler_file.write(serializer.to_string())

    write_unlock(tiddler_base_filename)
    tiddler_file.close()

def list_recipes():
    path = os.path.join(store_root, 'recipes')
    recipes = _files_in_dir(path)

    return [Recipe(recipe) for recipe in recipes]

def list_bags():
    path = os.path.join(store_root, 'bags')
    bags = _files_in_dir(path)

    return [Bag(bag) for bag in bags]

def list_tiddler_revisions(tiddler):
    tiddler_base_filename = _tiddler_base_filename(tiddler)
    try: 
        revisions = sorted([int(x) for x in _files_in_dir(tiddler_base_filename)])
    except OSError, e:
        raise NoTiddlerError, 'unable to list revisions in tiddler: %s' % e
    revisions.reverse()
    return revisions

def write_lock(filename):
    """
    Make a lock file based on a filename.
    """

    lock_filename = _lock_filename(filename)

    if os.path.exists(lock_filename):
        pid = _read_lock_file(lock_filename)
        raise StoreLockError, 'write lock for %s taken by %s' % (filename, pid)

    lock = open(lock_filename, 'w')
    pid = os.getpid()
    lock.write(str(pid))
    lock.close

def write_unlock(filename):
    """
    Unlock the write lock.
    """
    lock_filename = _lock_filename(filename)
    os.unlink(lock_filename)

def _bag_path(bag_name):
    return os.path.join(store_root, 'bags', bag_name)

def _files_in_dir(path):
    return filter(lambda x: not x.startswith('.'), os.listdir(path))

def _lock_filename(filename):
    pathname, basename = os.path.split(filename)
    lock_filename = os.path.join(pathname, '.%s' % basename)
    return lock_filename

def _read_lock_file(lockfile):
    lock = open(lockfile, 'r')
    pid = lock.read()
    lock.close()
    return pid

def _read_tiddler_file(tiddler, tiddler_filename):
    tiddler_file = codecs.open(tiddler_filename, encoding='utf-8')
    serializer = Serializer('text')
    serializer.object = tiddler
    tiddler_string = tiddler_file.read()
    tiddler_file.close()
    tiddler = serializer.from_string(tiddler_string)
    return tiddler

def _read_tiddler_revision(tiddler, index=0):
    tiddler_base_filename = _tiddler_base_filename(tiddler)
    tiddler_revision = _tiddler_revision_filename(tiddler, index=index)
    tiddler_filename = os.path.join(tiddler_base_filename, str(tiddler_revision))
    tiddler = _read_tiddler_file(tiddler, tiddler_filename)
    tiddler.revision = tiddler_revision
    return tiddler

def _read_policy(bag_path):
    policy_filename = os.path.join(bag_path, 'policy')
    policy_file = codecs.open(policy_filename, encoding='utf-8')
    policy = policy_file.read()
    policy_file.close()
    policy_data = simplejson.loads(policy)
    policy = Policy()
    for key, value in policy_data.items():
        policy.__setattr__(key, value)
    return policy

def _recipe_path(recipe):
    return os.path.join(store_root, 'recipes', recipe.name)

def _tiddler_base_filename(tiddler):
    # should be get a Bag or a name here?
    bag_name = tiddler.bag

    store_dir = _tiddlers_dir(bag_name)

    if not os.path.exists(store_dir):
        raise NoBagError, "%s does not exist" % store_dir

    return os.path.join(store_dir, tiddler.title)

def _tiddlers_dir(bag_name):
    return os.path.join(_bag_path(bag_name), 'tiddlers')

def _tiddler_revision_filename(tiddler, index=0):
    revision = 0
    if tiddler.revision:
        revision = tiddler.revision
    else:
        revisions = list_tiddler_revisions(tiddler)
        if revisions:
            revision = revisions[index]
    return int(revision)

def _write_policy(policy, bag_path):
    policy_dict = {}
    for key in ['read','write','create','delete','manage','owner']:
        policy_dict[key] = policy.__getattribute__(key)
    policy_string = simplejson.dumps(policy_dict)
    policy_filename = os.path.join(bag_path, 'policy')
    policy_file = codecs.open(policy_filename, 'w', encoding='utf-8')
    policy_file.write(policy_string)
    policy_file.close()

