"""
Test search via the web.
"""


import httplib2
import simplejson

from fixtures import muchdata, reset_textstore, _teststore, initialize_app

def setup_module(module):
    initialize_app()
    reset_textstore()
    module.store = _teststore()
    muchdata(module.store)

def test_simple_search():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/search?q=tiddler%200',
            headers={'User-Agent': 'Mozilla'},
            method='GET')

    assert response['status'] == '200'

def test_title_search():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/search?q=tiddler0',
            method='GET')

    assert response['status'] == '200'

def test_malformed_search():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/search',
            method='GET')

    assert response['status'] == '400'

def test_json_search():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/search.json?q=tiddler%200',
            method='GET')

    assert response['status'] == '200'
    assert 'json' in response['content-type']
    info = simplejson.loads(content)
    assert len(info) == 30

def test_json_search_filtered():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/search.json?q=tiddler%200;select=tag:tagtwo',
            method='GET')

    assert response['status'] == '200'
    assert 'json' in response['content-type']
    info = simplejson.loads(content)
    assert len(info) == 30

def test_funky_encoding():
    http = httplib2.Http()
    response, content = http.request(
            'http://our_test_domain:8001/search?q=title:\"\xd3ptica%20electromagn\xe9tica\"')
    assert response['status'] == '400', content
