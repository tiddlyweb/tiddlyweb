
"""
Test that GETting a recipe in wiki form, gets a tiddlywiki.
"""

import sys
sys.path.append('.')

from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2

from fixtures import muchdata

from tiddlyweb.store import Store
from tiddlyweb.web import negotiate

def setup_module(module):
    from tiddlyweb.web import serve
    # we have to have a function that returns the callable,
    # Selector just _is_ the callable
    def app_fn():
        return serve.default_app('urls.map')
    #wsgi_intercept.debuglevel = 1
    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('our_test_domain', 8001, app_fn)

    module.store = Store('text')
    muchdata(module.store)

def test_get_recipe_wiki():
    """
    Return a wiki for a recipe we can access.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long.wiki',
            method='GET')

    assert response['status'] == '200', 'response status should be 200'
    assert 'i am tiddler 8' in content, 'wiki contains tiddler 8'

def test_get_recipe_txt():
    """
    Return a wiki for a recipe we can access.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long.txt',
            method='GET')

    assert response['status'] == '200', 'response status should be 200'
    assert '/bags/bag8?tiddler8' in content, 'recipe contains tiddler 8 from bag 8'

def test_get_missing_recipe():
    """
    Return 404 for a recipe that is not there.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/not_there',
            method='GET')

    assert response['status'] == '404', 'response status should be 404'

def test_get_recipe_tiddler_list():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers',
            method='GET')

    assert response['status'] == '200', 'response status should be 200'
    assert len(content.rstrip().split('\n')) == 5, 'len tiddlers should be 5 is %s' % len(content.split('\n'))

def test_get_recipes():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes',
            method='GET')

    assert response['status'] == '200', 'response status should be 200'
