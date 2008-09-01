"""
A class representing a simple user entity.
"""

from crypt import crypt

class User(object):
    """
    A simple representation of a user. For now
    a user is simply a username, an optional
    password, an optional list of roles,
    and an optional note.

    This is all subject to change.
    """

    def __init__(self, usersign, note=None):
        self.usersign = usersign
        self.note = note
        self._password = None
        self.roles = set()

    def has_role(self, role):
        return role in self.roles

    def add_role(self, role):
        self.roles.add(role)

    def del_role(self, role):
        self.roles.discard(role)

    def list_roles(self):
        return list(self.roles)

    def set_password(self, password):
        password = password.strip()
        self._password = crypt(password.strip(), 'salty')

    def check_password(self, candidate_password):
        if self._password is None:
            return False
        crypted_thing = crypt(candidate_password.strip(), self._password)
        return crypted_thing == self._password

    def __repr__(self):
        return self.usersign + ' ' + object.__repr__(self)

