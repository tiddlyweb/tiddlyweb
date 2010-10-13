
from wsgi_intercept import httplib2_intercept
from base64 import b64encode
import wsgi_intercept
import urllib
import httplib2
import simplejson

from fixtures import reset_textstore, _teststore
from tiddlyweb.model.recipe import Recipe

def setup_module(module):
    from tiddlyweb.web import serve
    # we have to have a function that returns the callable,
    # Selector just _is_ the callable
    def app_fn():
        return serve.load_app()
    #wsgi_intercept.debuglevel = 1
    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('our_test_domain', 8001, app_fn)

    reset_textstore()
    module.store = _teststore()

    for i in xrange(5):
        recipe = Recipe('recipe%s' % i)
        recipe.set_recipe([('monkey', '')])
        module.store.put(recipe)

def test_get_recipes_txt():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes',
            headers={'Accept': 'text/plain'},
            method='GET')

    assert response['status'] == '200'
    for i in xrange(5):
        assert 'recipe%s\n' % i in content

def test_get_recipes_filters():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes?select=name:recipe1',
            headers={'Accept': 'text/plain'},
            method='GET')

    assert response['status'] == '200', content
    assert 'recipe1\n' in content
    assert 'recipe2\n' not in content

def test_get_recipes_filters_bad_select():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes?select=text:recipe1',
            headers={'Accept': 'text/plain'},
            method='GET')

    assert response['status'] == '400', content
    assert 'malformed filter' in content
    assert "object has no attribute 'text'" in content

def test_get_recipes_filters_rbag():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes?select=rbag:monkey',
            headers={'Accept': 'text/plain'},
            method='GET')

    assert response['status'] == '200', content
    assert 'recipe0' in content

def test_get_recipes_selected_sorted_filters():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes?select=name:>recipe2',
            headers={'Accept': 'text/plain'},
            method='GET')

    assert response['status'] == '200', content
    assert 'recipe1\n' not in content
    assert 'recipe2\n' not in content
    assert 'recipe3\n' in content

def test_get_recipes_sorted_filters():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes?sort=-name',
            headers={'Accept': 'text/plain'},
            method='GET')

    assert response['status'] == '200', content
    assert 'recipe4\nrecipe3\nrecipe2\nrecipe1\nrecipe0' in content

def test_get_recipes_sorted_limitedfilters():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes?sort=-name;limit=1,1',
            headers={'Accept': 'text/plain'},
            method='GET')

    assert response['status'] == '200', content
    assert content == 'recipe3\n'
