"""
The ChallengerInterface class.
"""


class ChallengerInterface(object):
    """
    An interface for challenging users for authentication purposes.
    The chalenger basically does whatever is required and *may* result
    in doing something to a response that causes the user agent's next
    request to pass an :py:class:`extractor
    <tiddlyweb.web.extractors.ExtractorInterface>`.

    Though there is no requirement for there to be a one to one
    correspondence between a Challenger and an :py:class:`Extractor
    <tiddlyweb.web.extractors.ExtractorInterface>`, it will often be
    the case that a Challenger will need a particular Extractor
    in order to be effective.

    A Challenger is a WSGI application.
    """

    def challenge_get(self, environ, start_response):
        """
        Respond to a ``GET`` request.
        """
        pass

    def challenge_post(self, environ, start_response):
        """
        Respond to a ``POST`` request.
        """
        pass

    def _cookie_path(self, environ):
        """
        The path to which the cookie applies. This is ``<server_prefix>/``.
        """
        return environ['tiddlyweb.config']['server_prefix'] + '/'
