"""
def utilities in tiddlyweb.web.util
"""

from tiddlyweb.web.util import tiddler_url
from tiddlyweb.model.tiddler import Tiddler

from tiddlyweb.config import config

def setup_module(module):
    config['server_host'] = {'scheme': 'http',
            'host': 'our_test_domain', 'port': '8001'}
    module.environ = {'tiddlyweb.config': config}

def teardown_module(module):
    config['server_prefix'] = ''

def test_tiddler_url():
    tiddler = Tiddler('foobar')
    tiddler.bag = 'zoom'

    url = tiddler_url(environ, tiddler)

    assert url == 'http://our_test_domain:8001/bags/zoom/tiddlers/foobar'

    tiddler.recipe = 'car'

    url = tiddler_url(environ, tiddler, container='recipes')

    assert url == 'http://our_test_domain:8001/recipes/car/tiddlers/foobar'

    url = tiddler_url(environ, tiddler, container='recipes', full=False)

    assert url == '/recipes/car/tiddlers/foobar'

    config['server_prefix'] = '/sleep'

    url = tiddler_url(environ, tiddler, container='recipes', full=False)

    assert url == '/sleep/recipes/car/tiddlers/foobar'

    url = tiddler_url(environ, tiddler)

    assert url == 'http://our_test_domain:8001/sleep/bags/zoom/tiddlers/foobar'

    tiddler.fields['_canonical_uri'] = 'http://example.com'
    url = tiddler_url(environ, tiddler)

    assert url == 'http://example.com'
