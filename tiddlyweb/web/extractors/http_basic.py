"""
A very simple :py:class:`extractor
<tiddlyweb.web.extractors.ExtractorInterface>` that looks at the
HTTP ``Authorization`` header and looks for Basic auth information
therein.
"""

from base64 import b64decode

from tiddlyweb.web.extractors import ExtractorInterface


class Extractor(ExtractorInterface):
    """
    An :py:class:`extractor <tiddlyweb.web.extractors.ExtractorInterface>`
    for HTTP Basic Authentication. If there is an `Authorization` header
    attempt to get a username and password out of it and compare with
    :py:class:`User <tiddlyweb.model.user.User>` information in the
    :py:class:`Store <tiddlyweb.store.Store>`. If the password is valid,
    return the user information. Otherwise return ``False``.
    """

    def extract(self, environ, start_response):
        """
        Look in the request for an ``Authorization`` header.
        """
        user_info = environ.get('HTTP_AUTHORIZATION', None)
        if user_info is None:
            return False
        if user_info.startswith('Basic'):
            user_info = user_info.strip().split(' ')[1]
            decoded = b64decode(user_info.encode('utf-8')).decode('utf-8')
            candidate_username, password = decoded.split(':')
            user = self.load_user(environ, candidate_username)
            if user.check_password(password):
                return {"name": user.usersign, "roles": user.list_roles()}
        return False
