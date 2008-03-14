"""
Test that GETting a bag can list the tiddlers.
"""

import sys
sys.path.append('.')

from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2

from fixtures import muchdata

from tiddlyweb.store import Store

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
    muchdata(module.store)

def test_get_bag_tiddler_list_default():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers',
            method='GET')

    assert response['status'] == '200', 'response status should be 200'
    assert response['content-type'] == 'text/plain', 'response content-type should be text/plain is %s' % response['content-type']
    assert len(content.rstrip().split('\n')) == 10, 'len tiddlers should be 10 is %s' % len(content.split('\n'))

def test_get_bag_tiddler_list_text():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers.txt',
            method='GET')

    print content
    assert response['status'] == '200', 'response status should be 200'
    assert response['content-type'] == 'text/plain', 'response content-type should be text/plain is %s' % response['content-type']
    assert len(content.rstrip().split('\n')) == 10, 'len tiddlers should be 10 is %s' % len(content.split('\n'))

def test_get_bag_tiddler_list_html():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers.html',
            method='GET')

    print content
    assert response['status'] == '200', 'response status should be 200'
    assert response['content-type'] == 'text/html', 'response content-type should be text/html is %s' % response['content-type']
    assert len(content.rstrip().split('\n')) == 10, 'len tiddlers should be 10 is %s' % len(content.split('\n'))

def test_get_bag_tiddler_list_filtered():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers?tiddler8',
            method='GET')

    assert response['status'] == '200', 'response status should be 200'
    assert len(content.rstrip().split('\n')) == 1, 'len tiddlers should be 1 is %s' % len(content.rstrip().split('\n'))

def test_get_bags():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags',
            method='GET')

    assert response['status'] == '200', 'response status should be 200'
    assert len(content.rstrip().split('\n')) == 31, 'len tiddlers should be 32 is %s' % len(content.rstrip().split('\n'))

