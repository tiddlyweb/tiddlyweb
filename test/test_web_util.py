"""
Test utilities in tiddlyweb.web.util
"""

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from httpexceptor import HTTP400

from tiddlyweb.web.util import (tiddler_url, datetime_from_http_date,
        encode_name, bag_etag, recipe_etag, read_request_body)
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler

from tiddlyweb.config import config

import pytest


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

    # we decided url is always local
    #assert url == 'http://example.com'
    assert url == 'http://our_test_domain:8001/sleep/bags/zoom/tiddlers/foobar'


def test_bad_http_timestamp():
    assert datetime_from_http_date('0') is None


def test_encode_name():
    """
    Ensure encode name encodes similarly to JavaScript.
    """
    assert encode_name("~alpha's (.beta*)!") == "~alpha's%20(.beta*)!"


def test_read_request_body():
    data = 'content of handle'
    data_length = len(data)
    fh = StringIO(data)
    environ['wsgi.input'] = fh

    output = read_request_body(environ, data_length)
    assert output == data

    output = read_request_body(environ, data_length)
    assert output == ''

    fh.close()

    pytest.raises(HTTP400, 'read_request_body(environ, data_length)')


def test_bag_etag():
    """
    Explicitly test bag_etag method (not used by the core code).
    """
    bag1 = Bag('foo')
    bag1.desc = 'desc'
    bag2 = Bag('foo')
    bag2.desc = 'desc'

    assert bag_etag(environ, bag1) == bag_etag(environ, bag2)


def test_recipe_etag():
    """
    Explicitly test recipe_etag method (not used by the core code).
    """
    recipe1 = Recipe('foo')
    recipe1.desc = 'desc'
    recipe2 = Recipe('foo')
    recipe2.desc = 'desc'

    assert recipe_etag(environ, recipe1) == recipe_etag(environ, recipe2)
