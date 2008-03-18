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

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/html; charset=UTF-8', 'response content-type should be text/html;charset=UTF-8 is %s' % response['content-type']
    assert len(content.rstrip().split('\n')) == 12, 'len tiddlers should be 12 is %s' % len(content.split('\n'))

def test_get_bag_tiddler_list_text():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers.txt',
            method='GET')

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/plain; charset=UTF-8', 'response content-type should be text/plain; charset=UTF-8 is %s' % response['content-type']
    assert len(content.rstrip().split('\n')) == 10, 'len tiddlers should be 10 is %s' % len(content.split('\n'))

def test_get_bag_tiddler_list_html():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers.html',
            method='GET')

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/html; charset=UTF-8', 'response content-type should be text/html;charset=UTF-8 is %s' % response['content-type']
    assert len(content.rstrip().split('\n')) == 12, 'len tiddlers should be 12 is %s' % len(content.split('\n'))

def test_get_bag_tiddler_list_415():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers.gif',
            method='GET')

    assert response['status'] == '415', 'response status should be 415 is %s' % response['status']

def test_get_bag_tiddler_list_html_default():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers',
            method='GET', headers={'Accept': 'text/html'})

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/html; charset=UTF-8', 'response content-type should be text/html;charset=UTF-8 is %s' % response['content-type']
    assert len(content.rstrip().split('\n')) == 12, 'len tiddlers should be 12 is %s' % len(content.split('\n'))

def test_get_bag_tiddler_list_filtered():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers.txt?tiddler8',
            method='GET')

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert len(content.rstrip().split('\n')) == 1, 'len tiddlers should be 1 is %s' % len(content.rstrip().split('\n'))

def test_get_bags_default():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags',
            method='GET')

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/html; charset=UTF-8', 'response content-type should be text/html;charset=UTF-8 is %s' % response['content-type']
    assert len(content.rstrip().split('\n')) == 33, 'len tiddlers should be 33 is %s' % len(content.rstrip().split('\n'))

def test_get_bags_txt():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags.txt',
            method='GET')

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/plain; charset=UTF-8', 'response content-type should be text/plain; charset=UTF-8 is %s' % response['content-type']
    assert len(content.rstrip().split('\n')) == 31, 'len tiddlers should be 32 is %s' % len(content.rstrip().split('\n'))

def test_get_bags_html():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags.html',
            method='GET')

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/html; charset=UTF-8', 'response content-type should be text/html;charset=UTF-8 is %s' % response['content-type']
    assert len(content.rstrip().split('\n')) == 33, 'len tiddlers should be 33 is %s' % len(content.rstrip().split('\n'))

def test_get_bags_unsupported_neg_format():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags.gif',
            method='GET')

    assert response['status'] == '415', 'response status should be 415 is %s' % response['status']

def test_get_bags_unsupported_recipe_format():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags.json',
            method='GET')

    assert response['status'] == '415', 'response status should be 415 is %s' % response['status']

def test_get_bags_unsupported_recipe_format_with_accept():
    """
    Fails over to accept header.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags.json',
            method='GET', headers={'Accept': 'text/html'})

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/html; charset=UTF-8', 'response content-type should be text/html;charset=UTF-8 is %s' % response['content-type']

def test_get_bags_unsupported_neg_format_with_accept():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags.gif',
            method='GET', headers={'Accept': 'text/html'})

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/html; charset=UTF-8', 'response content-type should be text/html;charset=UTF-8 is %s' % response['content-type']
