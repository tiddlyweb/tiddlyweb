"""
Exploratory testing for storing tiddlers.

Prequisites:

    * We know which bag this tiddler belongs to.
    * We've already established authorization to write.

"""

import os
import sys
import shutil
sys.path.append('.')

from fixtures import bagone, bagfour, textstore, reset_textstore
from tiddlyweb.store import Store

expected_stored_filename = os.path.join(textstore.bag_store, 'bagone', 'tiddlers', 'TiddlerOne')

expected_stored_content = """title: TiddlerOne
modifier: AuthorOne
tags: tagone tagtwo

c tiddler one content
"""

def setup_module(module):
    """
    Need to clean up the store here.
    """
    reset_textstore()

def test_simple_save():
    """
    Save a tiddler to disk and make sure it is there.
    """

    store = Store('text')
    store.save(bagone, bagone.list_tiddlers()[0])

    assert os.path.exists(expected_stored_filename), \
            'path %s should be created' \
            % expected_stored_filename

    f = file(expected_stored_filename)
    content = f.read()

    assert content == expected_stored_content, \
            'stored content should be %s, got %s' \
            % (content, expected_stored_content)

def test_multiple_save():
    """
    Save all the tiddlers in a bag and make sure they are there.
    """

    reset_textstore()
    store = Store('text')
    store.save(bagfour, bagfour.list_tiddlers())

    stored_dir = os.path.join(textstore.bag_store, 'bagfour', 'tiddlers')
    assert len(os.listdir(stored_dir)) == 3, 'there should be 3 files in the tiddlers directory'


