"""
A place for handling the extraction of user credentials from incoming
requests. UserExtract passes to a stack of extractors. If an extractor
returns something other than None, we have found valid data with
which to set tiddlyweb.usersign.
"""
import logging


class UserExtract(object):
    """
    WSGI Middleware to set the User, if it can be
    found in the request.
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        userinfo = {"name": u'GUEST', "roles": []}

        extractors = environ['tiddlyweb.config']['extractors']
        candidate_userinfo = _try_extractors(environ,
                extractors, start_response)

        if candidate_userinfo:
            userinfo = candidate_userinfo
        environ['tiddlyweb.usersign'] = userinfo

        return self.application(environ, start_response)


def _try_extractors(environ, extractors, start_response):
    """
    Loop through the available extractors until
    one returns a usersign instead of undef, or we
    run out of extractors.
    """
    for extractor_name in extractors:
        try:
            imported_module = __import__('tiddlyweb.web.extractors.%s' %
                    extractor_name, {}, {}, ['Extractor'])
        except ImportError:
            try:
                imported_module = __import__(extractor_name, {}, {},
                        ['Extractor'])
            except ImportError, exc:
                raise ImportError('could not load extractor %s: %s' %
                        (extractor_name, exc))
        extractor = imported_module.Extractor()
        extracted_user = extractor.extract(environ, start_response)
        if extracted_user:
            logging.debug('UserExtract:%s found %s',
                    extractor_name, extracted_user)
            return extracted_user
    return False
