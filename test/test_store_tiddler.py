"""
Exploratory testing for storing tiddlers.

Prequisites:

    * We know which bag this tiddler belongs to.
    * We've already established authorization to write.

"""

import os
import sys
sys.path.append('.')

from fixtures import bagone, bagfour, textstore, reset_textstore
from tiddlyweb.store import Store
from tiddlyweb.tiddler import Tiddler

expected_stored_filename = os.path.join(textstore.bag_store, 'bagone', 'tiddlers', 'TiddlerOne')

expected_stored_content = """modifier: AuthorOne
tags: [[tag five]] tagone tagtwo

c tiddler one content
"""

def setup_module(module):
    """
    Need to clean up the store here.
    """
    reset_textstore()

def test_simple_put():
    """
    put a tiddler to disk and make sure it is there.
    """

    store = Store('text')
    store.put(bagone)
    tiddler = bagone.list_tiddlers()[0]
    tiddler.tags = ['tagone', 'tagtwo', 'tag five']
    store.put(tiddler)

    assert os.path.exists(expected_stored_filename), \
            'path %s should be created' \
            % expected_stored_filename

    f = file(expected_stored_filename)
    content = f.read()

    assert content == expected_stored_content, \
            'stored content should be %s, got %s' \
            % (expected_stored_content, content)

def test_simple_get():
    """
    get a tiddler that had been stored in bagfour
    """

    stored_tiddler = Tiddler(title='TiddlerOne')
    stored_tiddler.bag = 'bagone'
    store = Store('text')
    store.get(stored_tiddler)

    assert stored_tiddler.title == 'TiddlerOne', 'retrieved tiddler has correct title'
    assert stored_tiddler.bag == 'bagone', 'retrieve tiddler has correct bag'
    assert stored_tiddler.content == 'c tiddler one content\n', 'content is %s should b %s' % (stored_tiddler.content, 'c tiddler one content\n')

    assert sorted(stored_tiddler.tags) == ['tag five', 'tagone', 'tagtwo']

def test_multiple_put():
    """
    put all the tiddlers in a bag and make sure they are there.
    """

    reset_textstore()
    store = Store('text')
    store.put(bagfour)
    store.put(bagfour.list_tiddlers())

    stored_dir = os.path.join(textstore.bag_store, 'bagfour', 'tiddlers')
    assert len(os.listdir(stored_dir)) == 3, 'there should be 3 files in the tiddlers directory'

