"""
The System's Configuration, to be carried
around in the environ. Eventually this
be in a userside actual file.
"""

import os

# The server filters (the WSGI MiddleWare)
from tiddlyweb.web.negotiate import Negotiate
from tiddlyweb.web.query import Query
from tiddlyweb.web.extractor import UserExtract
from tiddlyweb.auth import PermissionsExceptor
from tiddlyweb.web.http import HTTPExceptor
from tiddlyweb.web.wsgi import StoreSet, EncodeUTF8, SimpleLog, HTMLPresenter


# A dict explaining the scheme, host and port of our server.
# FIXME: a hack to get the server.host set properly in outgoing
# wikis.
DEFAULT_CONFIG = {
        'server_store': ['text', {'store_root': 'store'}],
        'server_request_filters': [
            Query,
            StoreSet,
            UserExtract,
            Negotiate
            ],
        'server_response_filters': [
            HTMLPresenter,
            PermissionsExceptor,
            HTTPExceptor,
            EncodeUTF8,
            SimpleLog
            ],
        'server_host': {},
        'server_prefix': '',
        'extension_types': {
            'txt': 'text/plain',
            'html': 'text/html',
            'json': 'application/json',
            'wiki': 'text/x-tiddlywiki',
        },
        'serializers': {
            'text/x-tiddlywiki': ['wiki', 'text/html; charset=UTF-8'],
            'text/html': ['html', 'text/html; charset=UTF-8'],
            'text/plain': ['text', 'text/plain; charset=UTF-8'],
            'application/json': ['json', 'application/json; charset=UTF-8'],
            'default': ['html', 'text/html; charset=UTF-8'],
        },
        'extractors': [
            'http_basic',
            'simple_cookie',
            ],
        'auth_systems': [
            'cookie_form',
            'openid',
            ],
        # XXX this should come from a file
        'secret': 'this should come from a file',

        }

def read_config():
    """
    Read in a local configuration override, but only
    from the current working directory (for now). If the
    file can't be imported things will blow up and the
    server not run.

    What's expected in the override file is a dict with the
    name config.
    """
    from tiddlywebconfig import config as custom_config
    global config
    config = DEFAULT_CONFIG
    for key in custom_config:
        print 'k: %s' % key
        try:
            # If this config item is a dict, update to update it
            # XXX: using exceptions for conditionals, a bit squiffy?
            custom_config[key].keys()
            config[key].update(custom_config[key])
        except AttributeError:
            config[key] = custom_config[key]

if os.path.exists('tiddlywebconfig.py'):
    read_config()
else:
    config = DEFAULT_CONFIG

