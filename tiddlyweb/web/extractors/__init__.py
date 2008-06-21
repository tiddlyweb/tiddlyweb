
class ExtractorInterface(object):
    """
    An interface for user extraction.
    Given a WSGI environ, figure out if the
    request has a valid user. If it does, 
    return that usersign.

    If it doesn't return false.
    """

    def extract(self, environ, start_response):
        pass
