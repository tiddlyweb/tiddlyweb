"""
Simple functios for storing bags as textfile
on the filesystem.
"""

# get from config!
store_root = 'store'

import os

from tiddlyweb.serializer import Serializer

def bag_put(bag):

    bag_path = _bag_path(bag)
    tiddlers_dir = _tiddlers_dir(bag)

    if not os.path.exists(bag_path):
        os.mkdir(bag_path)

    if not os.path.exists(tiddlers_dir):
        os.mkdir(tiddlers_dir)

    _write_security_policy(bag, bag_path)

def bag_get(bag):
    pass

def _bag_path(bag):
    return os.path.join(store_root, 'bags', bag.name)

def _tiddlers_dir(bag):
    return os.path.join(_bag_path(bag), 'tiddlers')

def _write_security_policy(bag, bag_path):
    security_filename = os.path.join(bag_path, 'security_policy')
    security_file = file(security_filename, 'w')

    security_file.write(bag.policy)

    security_file.close()

def tiddler_put(bag, tiddler):

    store_dir = _tiddlers_dir(bag)

    tiddler_filename = os.path.join(store_dir, tiddler.title)
    tiddler_file = file(tiddler_filename, 'w')

    serializer = Serializer(tiddler, 'text')

    tiddler_file.write(serializer.to_string())

    tiddler_file.close()

def tiddler_get(bag, tiddler):
    pass

