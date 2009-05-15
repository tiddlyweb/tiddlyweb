"""
A built-in twanager plugin for setting up a new instance
of TiddlyWeb, to lighten the load on getting started.

Example:

    twanager instance foo

This will create a foo directory containing:

    * empty tiddlywebconfig.py
    * store directory with a system bag containing
      the important plugins (assuming text store is
      in default config.py)
"""

import os
import random
import sha
import time

from tiddlyweb.fromsvn import import_list
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.manage import make_command
from tiddlyweb.store import Store

CONFIG_NAME = 'tiddlywebconfig.py'


def _generate_secret():
    """
    Create a somewhat random secret to be used
    for message authentication.
    """
    digest = sha.sha(str(time.time()))
    digest.update(str(random.random()))
    digest.update('tiddlyweb and tiddlywiki are rad')
    return digest.hexdigest()


EMPTY_CONFIG = """# A basic config, make your own changes here.
# Run 'pydoc tiddlyweb.config' for information on changing the
# defaults.
config = {
    'secret': '%s',
}
""" % _generate_secret()


@make_command()
def instance(args):
    """Create a tiddlyweb instance with default plugins in the named directory: <dir>"""
    directory = args[0]
    if not directory:
        raise ValueError('you must provide the name of a directory')
    if os.path.exists(directory):
        raise IOError('Your chosen directory already exists. Choose a different name.')
    os.mkdir(directory)
    os.chdir(directory)
    bag_names = [bag for bag, tiddlers in config['instance_tiddlers']]
    [_make_bag(bag) for bag in bag_names]
    update(None)
    _make_bag('common')
    _make_recipe('default', bag_names + ['common'])
    _empty_config()


@make_command()
def update(args):
    """Update the default plugins in the current instance."""
    [import_list(bag, tiddlers) for bag, tiddlers in
            config['instance_tiddlers']]


def _empty_config():
    """Write an empty tiddlywebconfig.py to the CWD."""
    cfg = open(CONFIG_NAME, 'w')
    cfg.write(EMPTY_CONFIG)
    cfg.close()


def _make_recipe(recipe_name, bags):
    """Make a recipe with recipe_name."""
    recipe = Recipe(recipe_name)
    recipe_list = [[bag, ''] for bag in bags]
    recipe.set_recipe(recipe_list)
    store = Store(config['server_store'][0], environ={'tiddlyweb.config': config})
    store.put(recipe)


def _make_bag(bag_name):
    """Make a bag with name bag_name to the store."""
    bag = Bag(bag_name)
    store = Store(config['server_store'][0], environ={'tiddlyweb.config': config})
    store.put(bag)


def init(config_in):
    """Initialize the plugin with config."""
    global config
    config = config_in
