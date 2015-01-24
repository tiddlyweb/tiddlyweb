"""
Properly handle tiddlywiki5 application/x-tiddler-dictionary
format.
"""

import simplejson

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler

from .fixtures import (reset_textstore, _teststore, initialize_app,
        get_http)


TEST_TEXT = 'cow: house\nfood: new'
TEST_TYPE = 'application/x-tiddler-dictionary'


def setup_module(module):
    initialize_app()

    reset_textstore()
    module.store = _teststore()
    module.http = get_http()

    module.store.put(Bag('holder'))


def test_put_x_tiddler_dictionary():
    data = {
        'text': TEST_TEXT,
        'type': TEST_TYPE,
    }
    json_data = simplejson.dumps(data)

    response, content = http.requestU(
            'http://our_test_domain:8001/bags/holder/tiddlers/dict1',
            headers={'Content-Type': 'application/json'},
            method='PUT',
            body=json_data)

    assert response['status'] == '204'

    tiddler = Tiddler('dict1', 'holder')
    tiddler = store.get(tiddler)
    assert tiddler.type == TEST_TYPE
    assert tiddler.text == TEST_TEXT


def test_get_x_tiddler_dictionary():
    response, content = http.requestU(
            'http://our_test_domain:8001/bags/holder/tiddlers/dict1',
            headers={'Accept': 'application/json'})

    assert response['status'] == '200'
    assert response['content-type'] == 'application/json'

    data = simplejson.loads(content)
    assert data['type'] == TEST_TYPE
    assert data['text'] == TEST_TEXT
