"""
Test that GETting a bag can list the tiddlers.
"""


import httplib2
import py.test

import tiddlyweb.web
import tiddlyweb.web.util
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.bag import Bag
from tiddlyweb.web import serve

from test.simpleplugin import PluginHere

from fixtures import initialize_app

expected_content="""<ul id="root" class="listing">
<li><a href="/recipes">recipes</a></li>
<li><a href="/bags">bags</a></li>
</ul>"""

def setup_module(module):
    initialize_app()

def test_get_root():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/',
            method='GET')

    assert response['status'] == '200'
    assert response['content-type'] == 'text/html; charset=UTF-8'
    assert expected_content in content

def test_head_root():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/',
            method='HEAD')

    assert response['status'] == '200'
    assert response['content-type'] == 'text/html; charset=UTF-8'
    assert content == ''

def test_with_header_and_css():
    from tiddlyweb.config import config
    config['css_uri'] = 'http://example.com/example.css'
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/', method='GET',
            headers={'User-Agent': 'Mozilla/5'})
    assert response['status'] == '200'
    assert 'link rel="stylesheet" href="http://example.com/example.css"' in content

def test_missing_system_plugin():
    from tiddlyweb.config import config
    config['system_plugins'] = ['missingplugin']
    py.test.raises(ImportError, 'serve.load_app()')
    config['system_plugins'] = []

def test_existing_system_plugin():
    from tiddlyweb.config import config
    config['system_plugins'] = ['test.simpleplugin']
    py.test.raises(PluginHere, 'serve.load_app()')
    config['system_plugins'] = []

def test_recipe_url():
    environ = {'tiddlyweb.config': {'server_host':  {'scheme':'http', 'host':'example.com', 'port': 80}}}
    recipe = Recipe('hello')

    assert tiddlyweb.web.util.recipe_url(environ, recipe) == 'http://example.com/recipes/hello'

def test_bag_url():
    bag = Bag('hello')
    environ = {'tiddlyweb.config': {'server_host':  {'scheme':'http', 'host':'example.com', 'port': 80}}}

    assert tiddlyweb.web.util.bag_url(environ, bag) == 'http://example.com/bags/hello'

def test_http_date_from_timestamp():
    timestamp = '200805231010'
    assert tiddlyweb.web.util.http_date_from_timestamp(timestamp) == 'Fri, 23 May 2008 10:10:00 GMT'

def test_http_date_from_timestamp_invalid():
    timestamp = '200702291010'
    badone = tiddlyweb.web.util.http_date_from_timestamp(timestamp)
    timestamp = '20 15'
    badtwo = tiddlyweb.web.util.http_date_from_timestamp(timestamp)
    assert badone[:14] == badtwo[:14]

    timestamp = '108502281010'
    py.test.raises(ValueError,
        'tiddlyweb.web.util.http_date_from_timestamp(timestamp)')

def test_datetime_from_http_date():
    timestamp = '200805231010'
    datestring = tiddlyweb.web.util.http_date_from_timestamp(timestamp)
    datetime_object = tiddlyweb.web.util.datetime_from_http_date(datestring)
    new_timestamp = datetime_object.strftime('%Y%m%d%H%M')
    assert '2008' in datestring
    assert 'May' in datestring
    assert new_timestamp == timestamp

def test_datetime_from_http_date_semi():
    """
    IE likes to send a length attribute with the http date on an If-Modified-Since.
    """
    timestamp = '200805231010'
    datestring = tiddlyweb.web.util.http_date_from_timestamp(timestamp)
    datestring = datestring + "; length=443333"
    datetime_object = tiddlyweb.web.util.datetime_from_http_date(datestring)
    new_timestamp = datetime_object.strftime('%Y%m%d%H%M')
    assert new_timestamp == timestamp

def test_datetime_form_http_date_utc():
    datestring = 'Wed, 09 Mar 2011 00:00:00 UTC'
    timestamp = '201103090000'
    datetime_object = tiddlyweb.web.util.datetime_from_http_date(datestring)
    new_timestamp = datetime_object.strftime('%Y%m%d%H%M')
    assert new_timestamp == timestamp
