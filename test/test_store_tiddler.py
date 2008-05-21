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
from tiddlyweb.store import Store, StoreLockError
from tiddlyweb.tiddler import Tiddler
import tiddlyweb.stores.text as texter
import py.test

expected_stored_filename = os.path.join(textstore.bag_store, 'bagone', 'tiddlers', 'TiddlerOne', '1')

expected_stored_text = """modifier: AuthorOne
created: 
modified: 200803030303
tags: tagone tagtwo [[tag five]]

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
    tiddler.modified = '200803030303'
    store.put(tiddler)

    assert os.path.exists(expected_stored_filename), \
            'path %s should be created' \
            % expected_stored_filename

    f = file(expected_stored_filename)
    text = f.read()

    assert text == expected_stored_text, \
            'stored text should be %s, got %s' \
            % (expected_stored_text, text)

def test_simple_get():
    """
    get a tiddler that had been stored in bagfour
    """

    stored_tiddler = Tiddler(title='TiddlerOne')
    stored_tiddler.bag = 'bagone'
    stored_tiddler.modified = '200803030303'
    store = Store('text')
    store.get(stored_tiddler)

    assert stored_tiddler.title == 'TiddlerOne', 'retrieved tiddler has correct title'
    assert stored_tiddler.bag == 'bagone', 'retrieve tiddler has correct bag'
    assert stored_tiddler.text == 'c tiddler one content', 'text is %s should b %s' % (stored_tiddler.text, 'c tiddler one content\n')

    assert sorted(stored_tiddler.tags) == ['tag five', 'tagone', 'tagtwo']

def test_get_revision():
    """
    Test we are able to retrieve a particular revision.
    """

    store = Store('text')
    store.put(bagone)
    tiddler = Tiddler(title='RevisionTiddler', text='how now 1')
    tiddler.bag = 'bagone'
    store.put(tiddler)
    tiddler.text = 'how now 2'
    store.put(tiddler)
    tiddler.text = 'how now 3'
    store.put(tiddler)

    tiddler = Tiddler(title='RevisionTiddler', bag='bagone')
    store.get(tiddler)

    assert tiddler.text == 'how now 3'
    assert tiddler.revision == 3

    tiddler = Tiddler(title='RevisionTiddler', bag='bagone', revision=2)
    store.get(tiddler)

    assert tiddler.text == 'how now 2'
    assert tiddler.revision == 2

    revisions = store.list_tiddler_revisions(tiddler)
    assert len(revisions) == 3
    assert revisions[0] == 3

def test_store_lock():
    """
    Make the sure the locking system throws the proper lock.
    """

    texter.write_lock(textstore.bag_store)
    py.test.raises(StoreLockError, 'texter.write_lock(textstore.bag_store)')

    texter.write_lock(textstore.bag_store + '/bagone/tiddlers/foobar')
    tiddler = Tiddler('foobar', text='hello')
    tiddler.bag = 'bagone'
    store = Store('text')
    py.test.raises(StoreLockError, 'store.put(tiddler)')


