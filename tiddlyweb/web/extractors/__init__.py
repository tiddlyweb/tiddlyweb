"""
The ExtractorInterface class, used to extract and validate
information in web requests that may identify a user. Often,
but not always, that information was originally created by
a :py:class:`challenger <tiddlyweb.web.challengers.ChallengerInterface>`.
"""

from tiddlyweb.model.user import User
from tiddlyweb.store import NoUserError, StoreMethodNotImplemented


class ExtractorInterface(object):
    """
    An interface for user extraction.

    Given a WSGI environ, figure out if the request contains information
    which can be used to identify a valid user. If it does, return a dict
    including information about that user.

    If it doesn't return `False`.
    """

    def extract(self, environ, start_response):
        """
        Look at the incoming request and try to extract a user.
        """
        pass

    def load_user(self, environ, usersign):
        """
        Check the :py:class:`User <tiddlyweb.model.user.User>`  database
        in the :py:class:`store <tiddlyweb.store.Store>` for a user
        matching this usersign. The user is not required to exist, but if
        it does it can be used to get additional information about the
        user, such as roles.
        """
        user = User(usersign)
        try:
            store = environ['tiddlyweb.store']
            user = store.get(user)
        except (StoreMethodNotImplemented, NoUserError):
            pass
        return user
