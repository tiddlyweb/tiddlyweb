"""
Tests related to fixing and confirming

    https://github.com/tiddlyweb/tiddlyweb/issues/99

The idea is that we want to be able to get a tiddler containing
JSON as JSON and as a tiddler with JSON in it.
"""

import simplejson

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler

from .fixtures import (reset_textstore, _teststore, initialize_app,
        get_http)


def setup_module(module):
    initialize_app()

    reset_textstore()
    module.store = _teststore()
    module.http = get_http()

    module.store.put(Bag('holder'))


def test_tiddler_is_json():
    data = {'alpha': 'one', 'beta': 'two'}
    json_data = simplejson.dumps(data)
    tiddler = Tiddler('json1', 'holder')
    tiddler.type = 'application/json'
    tiddler.text = json_data
    store.put(tiddler)

    stored_tiddler = store.get(Tiddler('json1', 'holder'))

    assert stored_tiddler.type == 'application/json'
    assert stored_tiddler.text == json_data


def test_get_tiddler_as_default():
    response, content = http.requestU(
            'http://our_test_domain:8001/bags/holder/tiddlers/json1')

    assert response['status'] == '200'
    assert 'application/json' in response['content-type']
    assert '"alpha": "one"' in content
    assert '"text"' not in content

    response, content = http.requestU(
            'http://our_test_domain:8001/bags/holder/tiddlers/json1',
            headers={'Accept': 'application/json'})

    assert response['status'] == '200'
    assert 'application/json' in response['content-type']
    assert '"alpha": "one"' in content
    assert '"text"' not in content


def test_get_tiddler_as_tiddler():
    response, content = http.requestU(
            'http://our_test_domain:8001/bags/holder/tiddlers/json1',
            headers={'Accept': 'application/vnd.tiddlyweb+json'})

    assert response['status'] == '200'
    assert 'application/json' in response['content-type']
    assert r'\"alpha\": \"one\"' in content
    assert '"text"' in content


def test_put_tiddler_x_tiddler():
    json_internal_data = simplejson.dumps({'alpha': 'one', 'beta': 'one'})
    json_external_data = simplejson.dumps({'type': 'application/json',
        'text': json_internal_data})

    response, content = http.requestU(
            'http://our_test_domain:8001/bags/holder/tiddlers/json2',
            headers={'Content-Type': 'application/vnd.tiddlyweb+json'},
            method='PUT',
            body=json_external_data)

    assert response['status'] == '204'

    location = response['location']
    response, content = http.requestU(location,
            headers={'Accept': 'application/json'})
    assert response['status'] == '200'
    assert response['content-type'].startswith('application/json')
    assert '"alpha": "one"' in content

    response, content = http.requestU(location,
            headers={'Accept': 'application/vnd.tiddlyweb+json'})
    assert response['status'] == '200'
    assert response['content-type'].startswith('application/json')
    assert r'\"alpha\": \"one\"' in content


def test_put_tiddler_json():
    json_internal_data = simplejson.dumps({'alpha': 'one', 'beta': 'one'})
    json_external_data = simplejson.dumps({'type': 'application/json',
        'text': json_internal_data})

    response, content = http.requestU(
            'http://our_test_domain:8001/bags/holder/tiddlers/json3',
            headers={'Content-Type': 'application/json'},
            method='PUT',
            body=json_external_data)

    assert response['status'] == '204'

    location = response['location']
    response, content = http.requestU(location,
            headers={'Accept': 'application/json'})
    assert response['status'] == '200'
    assert response['content-type'].startswith('application/json')
    assert '"alpha": "one"' in content

    response, content = http.requestU(location,
            headers={'Accept': 'application/vnd.tiddlyweb+json'})
    assert response['status'] == '200'
    assert response['content-type'].startswith('application/json')
    assert r'\"alpha\": \"one\"' in content
