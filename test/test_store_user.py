
import os
import sys
sys.path.append('.')

import py.test

from fixtures import textstore, reset_textstore
from tiddlyweb.store import Store, NoUserError
from tiddlyweb.user import User

expected_stored_filename = os.path.join(textstore.user_store, 'cdent')

def setup_module(module):
    reset_textstore()

def test_simple_put():
    store = Store('text')
    user = User('cdent', auth_system='http_basic', note='foo')
    store.put(user)

    assert os.path.exists(expected_stored_filename)

def test_simple_get():
    store = Store('text')
    user = User('cdent')
    store.get(user)

    assert user.note == 'foo'

def test_failed_get():
    store = Store('text')
    py.test.raises(NoUserError, 'store.get(User("nothere"))')
