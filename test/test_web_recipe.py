
"""
Test that GETting recipes.
"""


from wsgi_intercept import httplib2_intercept
from base64 import b64encode
import wsgi_intercept
import urllib
import httplib2
import simplejson

from fixtures import muchdata, reset_textstore, _teststore
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.user import User

authorization = b64encode('cdent:cowpig')

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
    muchdata(module.store)

    user = User('cdent')
    user.set_password('cowpig')
    module.store.put(user)

def test_get_recipe_txt():
    """
    Return a wiki for a recipe we can access.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long.txt',
            method='GET')

    assert response['status'] == '200'
    assert '/bags/bag8/tiddlers?select=title:tiddler8' in content

def test_get_recipe_not():
    """
    Return a 404 when content type not regonized.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long.xml',
            method='GET')

    assert response['status'] == '404'

def test_get_recipe_dot_name():
    """
    Effectively return an entity with a dot in the name.
    """
    recipe = Recipe('long.gif')
    recipe.desc = u'hello'
    store.put(recipe)

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long.gif',
            method='GET')

    assert response['status'] == '200'

    store.delete(recipe)

def test_get_recipe_not_with_accept():
    """
    Return a default content type when the extension and
    content type conflict.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long.html',
            method='GET', headers={'Accept': 'text/plain'})

    assert response['status'] == '200'

def test_get_missing_recipe():
    """
    Return 404 for a recipe that is not there.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/not_there',
            method='GET')

    assert response['status'] == '404'

def test_get_recipe_tiddler_list():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers',
            method='GET')

    assert response['status'] == '200'
    assert content.count('<li>') == 10

def test_get_recipe_tiddler_list_disposition():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers?download=long.html',
            method='GET')

    assert response['status'] == '200'
    assert response['content-disposition'] == 'attachment; filename="long.html"'

def test_get_recipe_tiddler_list_filtered_one():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers.txt?select=title:tiddler8',
            method='GET')

    assert response['last-modified'] == 'Fri, 23 May 2008 03:03:00 GMT'
    assert response['status'] == '200'
    assert content == 'tiddler8'

def test_get_recipe_tiddler_list_filtered_empty():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers.txt?select=title:tiddlerfoo',
            method='GET')

    assert response['status'] == '200'

def test_get_recipe_tiddler_list_bogus_filter():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers.txt?sort=monkey',
            method='GET')
    assert response['status'] == '400'
    assert 'malformed filter' in content

def test_get_recipes_default():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes',
            method='GET')

    assert response['status'] == '200'
    assert response['content-type'] == 'text/html; charset=UTF-8', 'response content-type should be text/html; charset=UTF-8 is %s' % response['content-type']
    assert content.count('<li>') == 1
    assert content.count('recipes/long') == 1

def test_get_recipes_txt():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes.txt',
            method='GET')

    assert response['status'] == '200'
    assert response['content-type'] == 'text/plain; charset=UTF-8', 'response content-type should be text/plain; charset=UTF-8 is %s' % response['content-type']
    assert len(content.rstrip().split('\n')) == 1, 'len recipe should be 1 is %s' % len(content.rstrip().split('\n'))

def test_get_recipes_json():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes.json',
            method='GET')

    assert response['status'] == '200'
    assert response['content-type'] == 'application/json; charset=UTF-8', \
            'response content-type should be application/json; charset=UTF-8 is %s' % response['content-type']
    info = simplejson.loads(content)
    assert type(info) == list
    assert len(info) == 1
    assert info[0] == 'long'

def test_get_recipes_unsupported_neg_format():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes.gif',
            method='GET')

    assert response['status'] == '415'

def test_get_recipes_unsupported_neg_format_with_accept():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes.gif',
            method='GET', headers={'Accept': 'text/html'})

    assert response['status'] == '200'
    assert response['content-type'] == 'text/html; charset=UTF-8', 'response content-type should be text/html;charset=UTF-8 is %s' % response['content-type']

def test_put_recipe():
    """
    Get a recipe as json then put it back with a different name.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long.json',
            method='GET')

    json = content
    assert response['status'] == '200'

    response, content = http.request('http://our_test_domain:8001/recipes/other',
            method='PUT', headers={'Content-Type': 'application/json'}, body=json)

    assert response['status'] == '204'
    assert response['location'] == 'http://our_test_domain:8001/recipes/other'

def test_put_bad_recipe():
    """
    Get a recipe as json then put it back with a different name.
    """
    http = httplib2.Http()

    response, content = http.request('http://our_test_domain:8001/recipes/other',
            method='PUT', headers={'Content-Type': 'application/json'},
            body='{ "recipe": null }')

    assert response['status'] == '400'
    assert 'malformed input' in content

def test_put_recipe_change_description():
    """
    Get a recipe as json then put it back with a different name.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long.json',
            method='GET')

    assert response['status'] == '200'

    info = simplejson.loads(content)
    info['desc'] = 'new description'
    json = simplejson.dumps(info)

    response, content = http.request('http://our_test_domain:8001/recipes/other',
            method='PUT', headers={'Content-Type': 'application/json'}, body=json)

    assert response['status'] == '204'
    assert response['location'] == 'http://our_test_domain:8001/recipes/other'

    response, content = http.request(response['location'],
            headers={'Accept': 'application/json'},
            method='GET')

    assert response['status'] == '200'

    info = simplejson.loads(content)
    assert info['desc'] == 'new description'

def test_put_recipe_415():
    """
    Get a recipe as text then fail to put it back as wiki.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long.txt',
            method='GET')

    text = content
    assert response['status'] == '200'

    response, content = http.request('http://our_test_domain:8001/recipes/other',
            method='PUT', headers={'Content-type': 'text/x-tiddlywiki'}, body=text)

    assert response['status'] == '415'

def test_delete_recipe():
    """
    DELETE the other recipe
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/other',
            method='DELETE')
    assert response['status'] == '204'

    response, content = http.request('http://our_test_domain:8001/recipes/other',
            method='GET')
    assert response['status'] == '404'

    # what happens when we delete the same recipe again?
    response, content = http.request('http://our_test_domain:8001/recipes/other',
            method='DELETE')
    assert response['status'] == '404'

def test_get_recipe_wiki_bag_constraints():
    """
    Make sure that when the constraints on a bag don't let read
    that a recipe with that bag throws an error.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers',
            method='GET')
    assert response['status'] == '200'

    _put_bag_policy('bag28', dict(policy=dict(read=['NONE'])))
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers',
            method='GET')
    assert response['status'] == '403'
    assert 'may not read' in content

def test_roundtrip_unicode_recipe():
    http = httplib2.Http()
    encoded_recipe_name = '%E3%81%86%E3%81%8F%E3%81%99'
    recipe_name = unicode(urllib.unquote(encoded_recipe_name), 'utf-8')
    assert type(recipe_name) == unicode
    recipe_list = [[recipe_name, '']]
    body = simplejson.dumps(dict(desc='',recipe=recipe_list))
    response, content = http.request('http://our_test_domain:8001/recipes/%s' % encoded_recipe_name,
            method='PUT', body=body.encode('utf-8'), headers={'Content-Type': 'application/json'})
    assert response['status'] == '204'

    recipe = Recipe(recipe_name)
    recipe = store.get(recipe)
    assert recipe.get_recipe() == recipe_list

    response, content = http.request('http://our_test_domain:8001/recipes/%s.json' % encoded_recipe_name,
            method='GET')
    assert response['status'] == '200'
    assert simplejson.loads(content)['recipe'] == recipe_list

def test_recipe_policy():
    http = httplib2.Http()
    recipe_dict = {
            'desc': 'hello',
            'policy': {'manage':['cdent'],'read':[]},
            'recipe': [['bag0','']],
            }
    recipe_json = simplejson.dumps(recipe_dict)

    response, content = http.request('http://our_test_domain:8001/recipes/boom', method='PUT',
            headers={'Content-Type': 'application/json'}, body=recipe_json)
    assert response['status'] == '204'

    response, content = http.request('http://our_test_domain:8001/recipes/boom', method='GET')
    assert response['status'] == '200'

    recipe_dict = {
            'desc': 'hello',
            'policy': {'manage':['cdent'],'read':['NONE']},
            'recipe': [['bag0','']],
            }
    recipe_json = simplejson.dumps(recipe_dict)

    response, content = http.request('http://our_test_domain:8001/recipes/boom', method='PUT',
            headers={'Content-Type': 'application/json', 'Authorization': 'Basic %s' % authorization},
            body=recipe_json)
    assert response['status'] == '204'

    response, content = http.request('http://our_test_domain:8001/recipes/boom', method='GET')
    assert response['status'] == '403'

    recipe_dict = {
            'desc': 'hello',
            'policy': {'manage':['NONE'],'read':['NONE']},
            'recipe': [['bag0','']],
            }
    recipe_json = simplejson.dumps(recipe_dict)
    response, content = http.request('http://our_test_domain:8001/recipes/boom', method='PUT',
            headers={'Content-Type': 'application/json', 'Authorization': 'Basic %s' % authorization},
            body=recipe_json)
    assert response['status'] == '204'

    recipe_dict = {
            'desc': 'hello',
            'policy': {'manage':['cdent'],'read':['NONE']},
            'recipe': [['bag0','']],
            }
    recipe_json = simplejson.dumps(recipe_dict)
    response, content = http.request('http://our_test_domain:8001/recipes/boom', method='PUT',
            headers={'Content-Type': 'application/json', 'Authorization': 'Basic %s' % authorization},
            body=recipe_json)
    assert response['status'] == '403'

def _put_bag_policy(bag_name, policy_dict):
    """
    XXX: This is duplicated from test_web_tiddler. Clean up!
    """
    json = simplejson.dumps(policy_dict)

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/%s' % bag_name,
            method='PUT', headers={'Content-Type': 'application/json'}, body=json)
    assert response['status'] == '204'
