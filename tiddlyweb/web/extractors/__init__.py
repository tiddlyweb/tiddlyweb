"""
The ExtractorInterface class.
"""

from tiddlyweb.model.user import User
from tiddlyweb.store import NoUserError, StoreMethodNotImplemented


class ExtractorInterface(object):
    """
    An interface for user extraction.
    Given a WSGI environ, figure out if the
    request has a valid user. If it does,
    return a hash including information
    about that user.

    If it doesn't return false.
    """

    def extract(self, environ, start_response):
        """
        Look at the incoming request and extract
        a user.
        """
        pass

    def load_user(self, environ, usersign):
        """
        Check the user database for this user, to get roles and such.
        """
        user = User(usersign)
        try:
            store = environ['tiddlyweb.store']
            user = store.get(user)
        except (StoreMethodNotImplemented, NoUserError):
            pass
        return user
