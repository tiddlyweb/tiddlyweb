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

    def __init__(self, usersign, note=None):
        self.usersign = usersign
        self.note = note

    def __repr__(self):
        return self.usersign + ' ' + object.__repr__(self)

