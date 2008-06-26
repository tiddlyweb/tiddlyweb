
# The System's Configuration, to be carried
# around in the environ. Eventually this
# be in an actual file.
config = {
        'server_store': ['text', {'store_root': 'store'}],
        'server_host': {},
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
            ]
        }
"""
A dict explaining the scheme, host and port of our server.
FIXME: a hack to get the server.host set properly in outgoing
wikis.
"""
