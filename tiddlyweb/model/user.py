"""
A class representing a simple user entity.
"""

from sha import sha


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

    def add_role(self, role):
        """
        Add the named role (a string) to this user.
        """
        self.roles.add(role)

    def del_role(self, role):
        """
        Remove the named role (a string) from this user.
        If it is not there, do nothing.
        """
        self.roles.discard(role)

    def list_roles(self):
        """
        List (as a list of strings) the roles that this
        user has.
        """
        return list(self.roles)

    def set_password(self, password):
        """
        Set the password for this user.
        """
        password = password.strip()
        self._password = sha(password.strip()).hexdigest()

    def check_password(self, candidate_password):
        """
        Check the password for this user. Return true if correct.
        """
        if self._password is None:
            return False
        crypted_thing = sha(candidate_password.strip()).hexdigest()
        return crypted_thing == self._password

    def __repr__(self):
        return self.usersign + ' ' + object.__repr__(self)
