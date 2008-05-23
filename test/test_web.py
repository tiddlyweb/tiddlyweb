"""
Test that GETting a bag can list the tiddlers.
"""

import sys
sys.path.append('.')

from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2
import py.test

import tiddlyweb.web
from tiddlyweb.recipe import Recipe
from tiddlyweb.bag import Bag

expected_content="""<html>
<head>
<title>TiddlyWeb</title>
</head>
<body>
<ul>
<li><a href="recipes">recipes</a></li>
<li><a href="bags">bags</a></li>
</ul>
<body>
</html>"""

def setup_module(module):
    from tiddlyweb.web import serve
    # we have to have a function that returns the callable,
    # Selector just _is_ the callable
    def app_fn():
        return serve.default_app('urls.map')
    #wsgi_intercept.debuglevel = 1
    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('our_test_domain', 8001, app_fn)

def test_get_root():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/',
            method='GET')

    assert response['status'] == '200'
    assert response['content-type'] == 'text/html; charset=UTF-8'
    assert content == expected_content

def test_recipe_url():
    environ = {'wsgi.url_scheme':'http', 'HTTP_HOST':'example.com'}
    recipe = Recipe('hello')

    assert tiddlyweb.web.recipe_url(environ, recipe) == 'http://example.com/recipes/hello'

def test_bag_url():
    environ = {'wsgi.url_scheme':'http', 'HTTP_HOST':'example.com'}
    bag = Bag('hello')

    assert tiddlyweb.web.bag_url(environ, bag) == 'http://example.com/bags/hello'

def test_http_date_from_timestamp():
    timestamp = '200805231010'
    assert tiddlyweb.web.http_date_from_timestamp(timestamp) == 'Fri, 23 May 2008 10:10:00 GMT'

def test_http_date_from_timestamp_invalid():
    timestamp = '200702291010'
    py.test.raises(ValueError, 'tiddlyweb.web.http_date_from_timestamp(timestamp)')

def test_http_date_from_timestamp_pre_1900():
    timestamp = '108502281010'
    py.test.raises(ValueError, 'tiddlyweb.web.http_date_from_timestamp(timestamp)')
