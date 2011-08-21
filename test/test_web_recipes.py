
from base64 import b64encode
import urllib
import httplib2
import simplejson

from fixtures import reset_textstore, _teststore, initialize_app
from tiddlyweb.model.recipe import Recipe

def setup_module(module):
    initialize_app()
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

    assert 'etag' in response
    etag = response['etag']

    response, content = http.request('http://our_test_domain:8001/recipes',
            headers={'Accept': 'text/plain', 'if-none-match': etag},
            method='GET')
    assert response['status'] == '304', content

    response, content = http.request('http://our_test_domain:8001/recipes',
            headers={'Accept': 'text/plain', 'if-none-match': etag + 'foo'},
            method='GET')
    assert response['status'] == '200', content

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
