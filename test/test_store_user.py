
import os

import py.test

import tiddlyweb.stores.text

from fixtures import reset_textstore, _teststore
from tiddlyweb.store import NoUserError
from tiddlyweb.model.user import User

expected_stored_filename = os.path.join('store', 'users', 'cdent')

def setup_module(module):
    reset_textstore()
    module.store = _teststore()

def test_simple_put():
    user = User('cdent', note='foo')
    user.set_password('cowpig')
    user.add_role('ADMIN')
    user.add_role('BOSS')
    store.put(user)

    if type(store.storage) != tiddlyweb.stores.text.Store:
        py.test.skip('skipping this test for non-text store')

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

    users = list(store.list_users())
    assert len(users) == 3
    usernames = [user.usersign for user in users]
    assert 'test1' in usernames
    assert 'test2' in usernames
    assert 'cdent' in usernames
    assert 'laramie' not in usernames

def test_delete_users():
    user = User('test1')
    store.delete(user)

    users = list(store.list_users())
    assert len(users) == 2
    usernames = [user.usersign for user in users]
    assert 'test1' not in usernames

def test_delete():
    user = User('deleteme')
    user.note = 'delete me please'
    store.put(user)

    stored_user = User('deleteme')
    stored_user = store.get(stored_user)
    assert stored_user.note == 'delete me please'

    deleted_user = User('deleteme')
    store.delete(deleted_user)

    py.test.raises(NoUserError, 'store.get(deleted_user)')
    py.test.raises(NoUserError, 'store.delete(deleted_user)')

def test_complex_username():
    username = u'test\u00BB\u00BBuser.com/foo'
    user = User(username)
    store.put(user)

    users = list(store.list_users())
    assert username in [user.usersign for user in users]

    user_out = User(username)
    user_out = store.get(user_out)
    assert user_out.usersign == username
