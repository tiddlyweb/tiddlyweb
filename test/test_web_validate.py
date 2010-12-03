"""
Test that GETting a tiddler in some form.
"""

import os

import httplib2
import simplejson

from base64 import b64encode

from fixtures import reset_textstore, _teststore, initialize_app

from tiddlyweb.model.user import User
from tiddlyweb.model.bag import Bag

authorization = b64encode('cdent:cowpig')

from tiddlyweb.web.validator import InvalidTiddlerError
import tiddlyweb.web.validator

def check_for_text(tiddler, environ):
    if 'foobar' not in tiddler.text:
        raise InvalidTiddlerError('missing "foobar" in tiddler.text')

def modify_text(tiddler, environ):
    tiddler.text = tiddler.text.replace('foobar', 'FOOBAR')

tiddlyweb.web.validator.TIDDLER_VALIDATORS = [
        check_for_text,
        modify_text,
        ]

def setup_module(module):
    initialize_app()
    reset_textstore()
    module.store = _teststore()

    bag = Bag('bag0')
    module.store.put(bag)

    user = User('cdent')
    user.set_password('cowpig')
    module.store.put(user)

def test_validate_one_tiddler():
    """No policy"""
    tiddler_json = '{"text": "barney is foobar"}'

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/barney',
            method='PUT', headers={'Content-Type': 'application/json'}, body=tiddler_json)

    assert response['status'] == '204'

    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/barney.txt',
            method='GET')

    assert response['status'] == '200'
    assert 'foobar' in content


def test_validate_one_tiddler_reject():
    """No policy"""
    bag = Bag('bag0')
    bag.policy.accept = ['NONE']
    store.put(bag)

    tiddler_json = '{"text": "barney is fobar"}'

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/barney',
            method='PUT', headers={'Content-Type': 'application/json'}, body=tiddler_json)

    assert response['status'] == '409'
    assert 'Tiddler content is invalid' in content

def test_validate_one_tiddler_modify():
    """No policy"""
    bag = Bag('bag0')
    bag.policy.accept = ['NONE']
    store.put(bag)

    tiddler_json = '{"text": "barney is foobar"}'

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/barney',
            method='PUT', headers={'Content-Type': 'application/json'}, body=tiddler_json)

    assert response['status'] == '204'

    location = response['location']
    response, content = http.request(location, method='GET')

    assert response['status'] == '200'
    assert 'FOOBAR' in content

def test_validate_one_bag():
    bag_json = simplejson.dumps(dict(desc='<script>alert("hot!");</script>', policy={}))

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag1',
            method='PUT', headers={'Content-Type': 'application/json'}, body=bag_json)

    assert response['status'] == '204'

    response, content = http.request('http://our_test_domain:8001/bags/bag1',
            method='GET')

    assert response['status'] == '200'

    assert '<script>' not in content
    assert '&lt;script' in content

def test_validate_one_recipe():
    recipe_json = simplejson.dumps(dict(desc='<script>alert("hot!");</script>', policy={}, recipe=[]))

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/recipe1',
            method='PUT', headers={'Content-Type': 'application/json'}, body=recipe_json)

    assert response['status'] == '204'

    response, content = http.request('http://our_test_domain:8001/recipes/recipe1',
            method='GET')

    assert response['status'] == '200'

    assert '<script>' not in content
    assert '&lt;script' in content
