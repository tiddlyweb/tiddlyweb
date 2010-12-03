"""
Test a full suite of unicode interactions.
"""


import urllib
import httplib2
import simplejson

from fixtures import muchdata, reset_textstore, _teststore, initialize_app
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag

encoded_name = 'aaa%25%E3%81%86%E3%81%8F%E3%81%99'
name = urllib.unquote(encoded_name).decode('utf-8')

def setup_module(module):
    initialize_app()
    reset_textstore()
    module.store = _teststore()
    #muchdata(module.store)

def test_put_unicode_bag():
    http = httplib2.Http()
    encoded_bag_name = encoded_name
    bag_name = name

    bag_policy = dict(delete=[bag_name])
    bag_json = simplejson.dumps({'policy':bag_policy})
    response, content = http.request('http://our_test_domain:8001/bags/%s' % encoded_bag_name,
            method='PUT', body=bag_json, headers={'Content-Type': 'application/json'})
    assert response['status'] == '204'

    bag = Bag(bag_name)
    bag = store.get(bag)
    assert bag.policy.delete == bag_policy['delete']
    assert bag.name == bag_name
    assert type(bag.name) == unicode

def test_put_unicode_tiddler():
    http = httplib2.Http()
    encoded_tiddler_name = encoded_name
    tiddler_name = name
    encoded_bag_name = encoded_name
    bag_name = name

    tiddler_text = u'hello %s' % name
    tiddler_json = simplejson.dumps(dict(modifier=name,text=tiddler_text,tags=[name]))
    response, content = http.request('http://our_test_domain:8001/bags/%s/tiddlers/%s' \
            % (encoded_bag_name, encoded_tiddler_name),
            method='PUT', body=tiddler_json, headers={'Content-Type':'application/json'})

    assert response['status'] == '204'

    tiddler = Tiddler(tiddler_name, bag=bag_name)
    tiddler = store.get(tiddler)
    assert tiddler.title == tiddler_name
    assert tiddler.text == tiddler_text
    assert tiddler.tags == [name]

def test_put_unicode_recipe():
    http = httplib2.Http()
    encoded_recipe_name = encoded_name
    recipe_name = name
    encoded_bag_name = encoded_name
    bag_name = name

    recipe_list = [[bag_name, '[tag[%s]]' % name]]
    json_recipe_list = simplejson.dumps(dict(recipe=recipe_list))
    response, content = http.request('http://our_test_domain:8001/recipes/%s' % encoded_recipe_name,
            method='PUT', body=json_recipe_list, headers={'Content-Type':'application/json'})
    assert response['status'] == '204'

    recipe = Recipe(recipe_name)
    recipe = store.get(recipe)
    assert recipe.get_recipe() == recipe_list
    assert recipe.name == recipe_name

def test_get_tiddlers_from_recipe():
    get_tiddlers_from_thing('recipes')

def test_get_tiddlers_from_bag():
    get_tiddlers_from_thing('bags')

def test_filter_tiddlers():
    http = httplib2.Http()

    response, content = http.request('http://our_test_domain:8001/bags/%s/tiddlers.json?select=tag:%s' \
            % (encoded_name, encoded_name),
            method='GET')
    assert response['status'] == '200'
    info = simplejson.loads(content)
    assert info[0]['tags'] == [name]
    assert info[0]['title'] == name
    assert info[0]['bag'] == name
    assert len(info) == 1

def get_tiddlers_from_thing(container):
    http = httplib2.Http()

    response, content = http.request('http://our_test_domain:8001/%s/%s/tiddlers.json' % (container, encoded_name),
            method='GET')
    assert response['status'] == '200'
    tiddler_info = simplejson.loads(content)
    assert tiddler_info[0]['title'] == name
    assert tiddler_info[0]['tags'] == [name]

    response, content = http.request('http://our_test_domain:8001/%s/%s/tiddlers/%s.json' \
            % (container, encoded_name, encoded_name),
            method='GET')
    assert response['status'] == '200'
    tiddler_info = simplejson.loads(content)
    assert tiddler_info['title'] == name
    assert tiddler_info['tags'] == [name]
    assert tiddler_info['text'] == 'hello %s' % name
