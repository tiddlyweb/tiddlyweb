"""
The ExtractorInterface class.
"""


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
