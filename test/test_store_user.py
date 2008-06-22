
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
    user = User('cdent', note='foo')
    user.set_password('cowpig')
    store.put(user)

    assert os.path.exists(expected_stored_filename)

def test_simple_get():
    store = Store('text')
    user = User('cdent')
    store.get(user)

    assert user.note == 'foo'
    assert user.check_password('cowpig')
    assert not user.check_password('pigcow')

def test_failed_get():
    store = Store('text')
    py.test.raises(NoUserError, 'store.get(User("nothere"))')
