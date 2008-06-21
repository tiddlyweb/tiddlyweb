

import Cookie

class UserExtract(object):
    """
    Stub WSGI Middleware to set the User, if it can be 
    found in the request.

    This is just crap to hold things together until
    we have the real thing.
    """
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        username = 'GUEST'

        candidate_username = self._try_extractors(environ, start_response)

        if candidate_username:
            username = candidate_username
        environ['tiddlyweb.usersign'] = username

        return self.application(environ, start_response)

    def _try_extractors(self, environ, start_response):
        for extractor_name in environ['tiddlyweb.config']['extractors']:
            try:
                imported_module = __import__('tiddlyweb.web.extractors.%s' % extractor_name,
                        {}, {}, ['Extractor'])
            except ImportError:
                try:
                    imported_module = __import__(extractor_name, {}, {}, ['Extractor'])
                except ImportError, e:
                    raise ImportError('could not load extractor %s: %s' % (extractor_name, e))
            extractor = imported_module.Extractor()
            extracted_user = extractor.extract(environ, start_response)
            if extracted_user:
                return extracted_user
        return False

