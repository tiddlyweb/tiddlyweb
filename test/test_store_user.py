
import os
import sys
sys.path.append('.')

import py.test

from fixtures import textstore, reset_textstore, teststore
from tiddlyweb.store import NoUserError
from tiddlyweb.model.user import User

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
    user = store.get(user)

    assert user.note == 'foo'
    assert user.check_password('cowpig')
    assert user.list_roles() == ['ADMIN', 'BOSS']
    assert not user.check_password('pigcow')

def test_failed_get():
    py.test.raises(NoUserError, 'store.get(User("nothere"))')

def test_list_users():
    user1 = User('test1')
    user2 = User('test2')
    store.put(user1)
    store.put(user2)

    users = store.list_users()
    assert len(users) == 3
    usernames = [user.usersign for user in users]
    assert 'test1' in usernames
    assert 'test2' in usernames
    assert 'cdent' in usernames
    assert 'laramie' not in usernames

def test_delete_users():
    user = User('test1')
    store.delete(user)

    users = store.list_users()
    assert len(users) == 2
    usernames = [user.usersign for user in users]
    assert 'test1' not in usernames
