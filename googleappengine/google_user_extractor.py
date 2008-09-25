"""
An extractor that looks for a google
user in the request.
"""

from tiddlyweb.web.extractors import ExtractorInterface
from google.appengine.api import users

import logging

class Extractor(ExtractorInterface):

    def extract(self, environ, start_response):
        user = users.get_current_user()
        logging.info('user gathered: %s' % user)

        if user:
            return {'name': user.nickname(), 'roles': []}
        return False


