
import os
import sys
sys.path.append('.')

import py.test

from fixtures import textstore, reset_textstore, teststore
from tiddlyweb.store import NoUserError
from tiddlyweb.user import User

expected_stored_filename = os.path.join(textstore.user_store, 'cdent')

def setup_module(module):
    reset_textstore()
    module.store = teststore()

def test_simple_put():
    user = User('cdent', note='foo')
    user.set_password('cowpig')
    user.add_role('ADMIN')
    user.add_role('BOSS')
    store.put(user)

    assert os.path.exists(expected_stored_filename)

def test_simple_get():
    user = User('cdent')
    store.get(user)

    assert user.note == 'foo'
    assert user.check_password('cowpig')
    assert user.list_roles() == ['ADMIN', 'BOSS']
    assert not user.check_password('pigcow')

def test_failed_get():
    py.test.raises(NoUserError, 'store.get(User("nothere"))')
