"""
Test GETting a tiddler revision list.
"""

import sys
sys.path.append('.')

from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2
import simplejson

from fixtures import muchdata, reset_textstore

from tiddlyweb.store import Store

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
        return serve.default_app('urls.map')
    #wsgi_intercept.debuglevel = 1
    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('our_test_domain', 8001, app_fn)

    module.store = Store('text')
    reset_textstore()
    muchdata(module.store)

def test_put_tiddler_txt_1():
    http = httplib2.Http()
    encoded_body = text_put_body.encode('UTF-8')
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers/TestOne',
            method='PUT', headers={'Content-Type': 'text/plain'}, body=encoded_body)

def test_put_tiddler_txt_2():
    http = httplib2.Http()
    encoded_body = text_put_body.encode('UTF-8')
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers/TestOne',
            method='PUT', headers={'Content-Type': 'text/plain'}, body=encoded_body)

def test_put_tiddler_txt_3():
    http = httplib2.Http()
    encoded_body = text_put_body.encode('UTF-8')
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers/TestOne',
            method='PUT', headers={'Content-Type': 'text/plain'}, body=encoded_body)

def test_get_tiddler_revision_list():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers/TestOne/revisions',
            method='GET')

    assert response['status'] == '200'
    assert '3' in content
    assert 'revisions' in content

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

