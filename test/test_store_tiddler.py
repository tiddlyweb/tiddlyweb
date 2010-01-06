"""
Exploratory testing for storing tiddlers.

Prequisites:

    * We know which bag this tiddler belongs to.
    * We've already established authorization to write.

"""

import os

from fixtures import bagfour, tiddlers, reset_textstore, _teststore
from tiddlyweb.config import config
from tiddlyweb.store import StoreLockError, NoTiddlerError, NoBagError
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.stores.text import Store as Texter
from tiddlyweb.util import write_lock, LockError

import py.test

expected_stored_filename = os.path.join('store', 'bags', 'bagone', 'tiddlers', 'TiddlerOne', '1')

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
    module.store = _teststore()

def test_simple_put():
    """
    put a tiddler to disk and make sure it is there.
    """
    bagone = Bag('bagone')
    bagone.add_tiddlers(tiddlers)

    store.put(bagone)
    tiddler = bagone.list_tiddlers()[0]
    print tiddler.revision
    tiddler.tags = ['tagone', 'tagtwo', 'tag five']
    tiddler.modified = '200803030303'
    store.put(tiddler)

    if type(store.storage) != Texter:
        py.test.skip('skipping this test for non-text store')
    
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

    bagone = Bag('bagone')
    bagone.add_tiddlers(tiddlers)

    store.put(bagone)
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

    if type(store.storage) != Texter:
        py.test.skip('skipping this test for non-text store')
    
    assert os.path.exists(os.path.join('store', 'bags', 'bagone', 'tiddlers', 'RevisionTiddler'))
    store.delete(tiddler)
    assert not os.path.exists(os.path.join('store', 'bags', 'bagone', 'tiddlers', 'RevisionTiddler'))

def test_failed_delete_not_there():
    tiddler = Tiddler(title='RevisionTiddler', bag='bagone')
    # in case we skipped deleting it above, delete it again
    try:
        store.delete(tiddler)
    except NoTiddlerError:
        pass
    py.test.raises(NoTiddlerError, 'store.delete(tiddler)')

def test_failed_delete_perms():
    tiddler = Tiddler(title='TiddlerOne', bag='bagone')

    if type(store.storage) != Texter:
        py.test.skip('skipping this test for non-text store')
    
    path = os.path.join('store', 'bags', 'bagone', 'tiddlers', 'TiddlerOne')
    assert os.path.exists(path)
    os.chmod(path, 0555)
    py.test.raises(IOError, 'store.delete(tiddler)')
    os.chmod(path, 0755)

def test_store_lock():
    """
    Make the sure the locking system throws the proper lock.
    """

    if type(store.storage) != Texter:
        py.test.skip('skipping this test for non-text store')
    
    write_lock('store/bags')
    py.test.raises(LockError, 'write_lock("store/bags")')

    write_lock('store/bags' + '/bagone/tiddlers/foobar')
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

def test_put_no_bag():
    tiddler = Tiddler('hi')
    py.test.raises(NoBagError, 'store.put(tiddler)')

def test_bad_filename():
    """
    If there is ../ in the tiddler name, choke.
    """
    if type(store.storage) != Texter:
        py.test.skip('skipping this test for non-text store')
    tiddler = Tiddler('../nastyone', 'bagone')
    py.test.raises(NoTiddlerError, 'store.put(tiddler)')
