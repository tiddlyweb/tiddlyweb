"""
Extract of user credentials from incoming web requests.
:py:class:`UserExtract` passes to a stack of extractors. If an
:py:class:`extractor <tiddlyweb.web.extractors.ExtractorInterface>`
returns something other than ``None``, we have found
valid data with which to set ``tiddlyweb.usersign``.
"""
import logging


LOGGER = logging.getLogger(__name__)


class UserExtract(object):
    """
    WSGI Middleware to set the ``tiddlyweb.usersign``, if it can
    be found in the request.
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
    one returns a usersign instead of None, or we
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
            except ImportError as exc:
                raise ImportError('could not load extractor %s: %s' %
                        (extractor_name, exc))
        extractor = imported_module.Extractor()
        extracted_user = extractor.extract(environ, start_response)
        if extracted_user:
            LOGGER.debug('UserExtract:%s found %s',
                    extractor_name, extracted_user)
            return extracted_user
    return False
