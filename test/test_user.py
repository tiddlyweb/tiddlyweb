"""
Test user, a simple data container for a user.
"""


import py.test

from tiddlyweb.model.user import User

usersign = 'cdent'
note = 'for future expansion'

def setup_module(module):
    pass

def test_user_create():
    user = User('cdent')
    assert type(user) == User

    assert user.usersign == 'cdent'
    user.note = note
    assert user.note == note

    user.note = 'bar'
    assert user.note == 'bar'

def test_user_args():
    py.test.raises(TypeError, 'user = User()')

def test_user_stringification():
    user = User('monkey')

    assert 'monkey' in '%s' % user

def test_user_password():
    user = User('monkey')
    user.set_password('cowpig')

    assert user.check_password('cowpig'), 'correct password returns true'
    assert not user.check_password('pigcow'), 'bad password returns false'

def test_empty_password():
    user = User('ape')
    assert not user.check_password('xow'), 'no password on user returns false'
    assert not user.check_password('')
    user.set_password('')
    assert not user.check_password('')

def test_user_role():
    user = User('paper')
    assert user.list_roles() == []

    user.add_role('ADMIN')
    assert user.list_roles() == ['ADMIN']

    user.del_role('ADMIN')
    assert user.list_roles() == []

# add twice to confirm set-ness
    user.add_role('ADMIN')
    user.add_role('ADMIN')

    assert user.list_roles() == ['ADMIN']

