"""
A class representing a simple user entity.
"""

class User(object):
    """
    A simple representation of a user. For now
    a user is simply a username, the name of their
    authentication mechanism, and a note.

    This is all subject to change.
    """

    default_auth_system = 'http_basic'

    def __init__(self, usersign, auth_system=default_auth_system, note=None):
        self.usersign = usersign
        self.auth_system = auth_system
        self.note = note

    def __repr__(self):
        return self.usersign + ' ' + object.__repr__(self)

