"""
Test extended fields on tiddlers via the HTTP API.
"""


import simplejson

from .fixtures import (reset_textstore, _teststore, muchdata, initialize_app,
        get_http)

http = get_http()


def setup_module(module):
    initialize_app()
    reset_textstore()
    module.store = _teststore()
    muchdata(module.store)


def test_put_tiddler_with_fields():
    tiddler_dict = {
            'tags': ['one', 'two', 'three'],
            'text': 'hello',
            'fields': {
                'server.first': 'base',
                'field1': 'value1',
                'field2': 'value2',
            },
    }
    tiddler_json = simplejson.dumps(tiddler_dict)

    response, content = http.requestU(
            'http://our_test_domain:8001/bags/bag0/tiddlers/feebles',
            method='PUT',
            headers={'Content-Type': 'application/json'},
            body=tiddler_json)

    assert response['status'] == '204'


def test_get_tiddler_with_fields():
    response, content = http.requestU(
            'http://our_test_domain:8001/bags/bag0/tiddlers/feebles.json',
            method='GET')

    assert response['status'] == '200'
    tiddler_dict = simplejson.loads(content)
    assert tiddler_dict['text'] == 'hello'
    assert tiddler_dict['uri'] == (
            'http://our_test_domain:8001/bags/bag0/tiddlers/feebles')
    assert tiddler_dict['fields']['field1'] == 'value1'
    assert tiddler_dict['fields']['field2'] == 'value2'
    assert 'server.first' not in tiddler_dict['fields']
