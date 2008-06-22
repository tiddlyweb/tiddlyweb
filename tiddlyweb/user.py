"""
A class representing a simple user entity.
"""

from crypt import crypt

class User(object):
    """
    A simple representation of a user. For now
    a user is simply a username, the name of their
    authentication mechanism, and a note.

    This is all subject to change.
    """

    def __init__(self, usersign, note=None):
        self.usersign = usersign
        self.note = note
        self._password = None

    def set_password(self, password):
        password = password.strip()
        self._password = crypt(password.strip(), 'salty')
        print self._password

    def check_password(self, candidate_password):
        if self._password is None:
            return False
        crypted_thing = crypt(candidate_password.strip(), self._password)
        print crypted_thing
        return crypted_thing == self._password

    def __repr__(self):
        return self.usersign + ' ' + object.__repr__(self)

