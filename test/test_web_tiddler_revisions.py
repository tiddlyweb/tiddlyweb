"""
Test GETting a tiddler revision list.
"""

import sys
sys.path.append('.')

from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2
import simplejson

from fixtures import muchdata, reset_textstore, teststore

text_put_body=u"""modifier: JohnSmith
created: 
modified: 200803030303
tags: [[tag three]]

Hello, I'm John Smith \xbb and I have something to sell.
"""

def setup_module(module):
    from tiddlyweb.web import serve
    # we have to have a function that returns the callable,
    # Selector just _is_ the callable
    def app_fn():
        return serve.load_app('our_test_domain', 8001, 'tiddlyweb/urls.map')
    #wsgi_intercept.debuglevel = 1
    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('our_test_domain', 8001, app_fn)

    module.store = teststore()
    reset_textstore()
    muchdata(module.store)

def test_put_tiddler_txt_1():
    http = httplib2.Http()
    encoded_body = text_put_body.encode('UTF-8')
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers/TestOne',
            method='PUT', headers={'Content-Type': 'text/plain'}, body=encoded_body)
    assert response['status'] == '204'

def test_put_tiddler_txt_2():
    http = httplib2.Http()
    encoded_body = text_put_body.encode('UTF-8')
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers/TestOne',
            method='PUT', headers={'Content-Type': 'text/plain'}, body=encoded_body)
    assert response['status'] == '204'

def test_put_tiddler_txt_3():
    http = httplib2.Http()
    encoded_body = text_put_body.encode('UTF-8')
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers/TestOne',
            method='PUT', headers={'Content-Type': 'text/plain'}, body=encoded_body)
    assert response['status'] == '204'
    assert response['etag'] == 'bag1/TestOne/3'

def test_get_tiddler_revision_list():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers/TestOne/revisions',
            method='GET')

    assert response['status'] == '200'
    assert '3' in content
    assert 'revisions' in content

def test_get_tiddler_revision_1():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers/TestOne/revisions/1',
            method='GET')
    assert response['status'] == '200'

def test_get_tiddler_revision_2():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers/TestOne/revisions/2',
            method='GET')
    assert response['status'] == '200'

def test_get_tiddler_revision_3():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers/TestOne/revisions/3',
            method='GET')
    assert response['status'] == '200'
    assert response['etag'] == 'bag1/TestOne/3'

def test_get_tiddler_revision_4_fail():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers/TestOne/revisions/4',
            method='GET')
    assert response['status'] == '404'

def test_get_tiddler_revision_list_404():
    """
    Get a 404 when the tiddler doesn't exist.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers/Test99/revisions',
            method='GET')

    assert response['status'] == '404'

def test_get_tiddler_not_revision_list():
    """
    When we retrieve a tiddler list we don't want their revision links.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers',
            method='GET')

    assert response['status'] == '200'
    assert '3' in content
    assert 'revisions' not in content

def test_get_tiddler_revision_list_json():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers/TestOne/revisions.json',
            method='GET')

    info = simplejson.loads(content)
    assert response['status'] == '200'
    assert len(info) == 3

def test_tiddler_revision_list_json_fat():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers/TestOne/revisions.json?fat=1',
            method='GET')

    info = simplejson.loads(content)
    assert response['status'] == '200'
    assert len(info) == 3
    assert info[0]['revision'] == 3
    assert 'I have something to sell' in info[0]['text']

    response, content = http.request('http://our_test_domain:8001/bags/bag28/tiddlers/tiddler0/revisions.json?previous=long:TestOne',
            method='POST', headers={'content-type': 'application/json'}, body=content)

    print content
    assert response['status'] == '204'
    assert response['location'] == 'http://our_test_domain:8001/bags/bag28/tiddlers/tiddler0'

    response, content = http.request('http://our_test_domain:8001/bags/bag28/tiddlers/tiddler0/revisions.json',
            method='GET')

    info = simplejson.loads(content)
    assert response['status'] == '200'

    assert info[0]['fields']['previous'] == 'long:TestOne'
