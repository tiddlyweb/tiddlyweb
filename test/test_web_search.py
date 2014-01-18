"""
Test search via the web.
"""


import sys
import simplejson

from .fixtures import (muchdata, reset_textstore, _teststore, initialize_app,
        get_http)

http = get_http()


def setup_module(module):
    initialize_app()
    reset_textstore()
    module.store = _teststore()
    muchdata(module.store)


def test_simple_search():
    response, content = http.request(
            'http://our_test_domain:8001/search?q=tiddler%200',
            headers={'User-Agent': 'Mozilla'},
            method='GET')

    assert response['status'] == '200'


def test_title_search():
    response, content = http.request(
            'http://our_test_domain:8001/search?q=tiddler0',
            method='GET')

    assert response['status'] == '200'


def test_malformed_search():
    response, content = http.request(
            'http://our_test_domain:8001/search',
            method='GET')

    assert response['status'] == '400'


def test_json_search():
    response, content = http.requestU(
            'http://our_test_domain:8001/search.json?q=tiddler%200',
            method='GET')

    assert response['status'] == '200'
    assert 'application/json' in response['content-type']
    info = simplejson.loads(content)
    assert len(info) == 30


def test_search_bad_ext():
    response, content = http.request(
            'http://our_test_domain:8001/search.monkey?q=tiddler%200',
            method='GET')

    assert response['status'] == '415'


def test_search_bad_ext_accept():
    response, content = http.request(
            'http://our_test_domain:8001/search.monkey?q=tiddler%200',
            method='GET',
            headers={'Accept': 'text/html'})

    assert response['status'] == '415'


def test_json_search_filtered():
    response, content = http.requestU(
            'http://our_test_domain:8001/search.json?q=tiddler%200;select=tag:tagtwo',
            method='GET')

    assert response['status'] == '200'
    assert 'application/json' in response['content-type']
    assert 'charset' not in response['content-type']
    info = simplejson.loads(content)
    assert len(info) == 30
