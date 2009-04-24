"""
Exploratory testing for storing tiddlers.

Prequisites:

    * We know which bag this tiddler belongs to.
    * We've already established authorization to write.

"""

import os
import sys
sys.path.append('.')

from fixtures import bagone, bagfour, textstore, reset_textstore, teststore
from tiddlyweb.config import config
from tiddlyweb.store import StoreLockError, NoTiddlerError
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.stores.text import Store as Texter
from tiddlyweb.util import write_lock, LockError
import tiddlyweb.stores.text as texter
import py.test

expected_stored_filename = os.path.join(textstore.bag_store, 'bagone', 'tiddlers', 'TiddlerOne', '1')

expected_stored_text = """modifier: AuthorOne
created: 
modified: 200803030303
type: None
tags: tagone tagtwo [[tag five]]

c tiddler one content
"""

def setup_module(module):
    """
    Need to clean up the store here.
    """
    reset_textstore()
    module.store = teststore()

def test_simple_put():
    """
    put a tiddler to disk and make sure it is there.
    """

    store.put(bagone)
    tiddler = bagone.list_tiddlers()[0]
    tiddler.tags = ['tagone', 'tagtwo', 'tag five']
    tiddler.modified = '200803030303'
    store.put(tiddler)

    assert os.path.exists(expected_stored_filename)

    f = file(expected_stored_filename)
    text = f.read()

    assert text == expected_stored_text

def test_simple_get():
    """
    get a tiddler that had been stored in bagfour
    """

    stored_tiddler = Tiddler(title='TiddlerOne')
    stored_tiddler.bag = 'bagone'
    stored_tiddler.modified = '200803030303'
    stored_tiddler = store.get(stored_tiddler)

    assert stored_tiddler.title == 'TiddlerOne', 'retrieved tiddler has correct title'
    assert stored_tiddler.bag == 'bagone', 'retrieve tiddler has correct bag'
    assert stored_tiddler.text == 'c tiddler one content', 'text is %s should b %s' % (stored_tiddler.text, 'c tiddler one content\n')

    assert sorted(stored_tiddler.tags) == ['tag five', 'tagone', 'tagtwo']

def test_get_revision():
    """
    Test we are able to retrieve a particular revision.
    """

    store.put(bagone)
    tiddler = Tiddler('RevisionTiddler')
    tiddler.text='how now 1'
    tiddler.bag = 'bagone'
    store.put(tiddler)
    tiddler.text = 'how now 2'
    store.put(tiddler)
    tiddler.text = 'how now 3'
    store.put(tiddler)

    tiddler = Tiddler(title='RevisionTiddler', bag='bagone')
    tiddler = store.get(tiddler)

    assert tiddler.text == 'how now 3'
    assert tiddler.revision == 3

    tiddler = Tiddler(title='RevisionTiddler', bag='bagone')
    tiddler.revision = 2
    tiddler = store.get(tiddler)

    assert tiddler.text == 'how now 2'
    assert tiddler.revision == 2

    revisions = store.list_tiddler_revisions(tiddler)
    assert len(revisions) == 3
    assert revisions[0] == 3

def test_delete():
    tiddler = Tiddler(title='RevisionTiddler', bag='bagone')

    assert os.path.exists(os.path.join(textstore.bag_store, 'bagone', 'tiddlers', 'RevisionTiddler'))
    store.delete(tiddler)
    assert not os.path.exists(os.path.join(textstore.bag_store, 'bagone', 'tiddlers', 'RevisionTiddler'))

def test_failed_delete_not_there():
    tiddler = Tiddler(title='RevisionTiddler', bag='bagone')
    py.test.raises(NoTiddlerError, 'store.delete(tiddler)')

def test_failed_delete_perms():
    tiddler = Tiddler(title='TiddlerOne', bag='bagone')
    path = os.path.join(textstore.bag_store, 'bagone', 'tiddlers', 'TiddlerOne')
    assert os.path.exists(path)
    os.chmod(path, 0555)
    py.test.raises(IOError, 'store.delete(tiddler)')
    os.chmod(path, 0755)

def test_store_lock():
    """
    Make the sure the locking system throws the proper lock.
    """

    texter = Texter(environ={'tiddlyweb.config': {'server_store': ['text', {'store_root': 'store'}]}})
    write_lock(textstore.bag_store)
    py.test.raises(LockError, 'write_lock(textstore.bag_store)')

    write_lock(textstore.bag_store + '/bagone/tiddlers/foobar')
    tiddler = Tiddler('foobar')
    tiddler.text='hello'
    tiddler.bag = 'bagone'
    py.test.raises(StoreLockError, 'store.put(tiddler)')

def test_put_with_slash():
    tiddler1 = Tiddler('He is 5 and 1/2', 'bagone')
    store.put(tiddler1)

    tiddler2 = Tiddler('He is 5 and 1/2', 'bagone')
    store.get(tiddler2)
    assert tiddler1.title == tiddler2.title

def test_bad_filename():
    """
    If there is ../ in the tiddler name, choke.
    """
    tiddler = Tiddler('../nastyone', 'bagone')
    py.test.raises(NoTiddlerError, 'store.put(tiddler)')
