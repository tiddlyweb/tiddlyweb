"""
Test that GETting a bag can list the tiddlers.
"""

import sys
sys.path.append('.')

from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2
import simplejson

from fixtures import muchdata, reset_textstore

from tiddlyweb.store import Store
from tiddlyweb.bag import Bag

policy_dict = dict(
        read=['chris','jeremy'],
        write=['chris','jeremy'],
        create=['chris','jeremy'],
        delete=['chris'],
        manage=['chris'],
        owner='chris')

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

def test_get_bag_tiddler_list_default():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers',
            method='GET')

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/html; charset=UTF-8', 'response content-type should be text/html;charset=UTF-8 is %s' % response['content-type']
    assert len(content.rstrip().split('\n')) == 12, 'len tiddlers should be 12 is %s' % len(content.split('\n'))

def test_get_bag_tiddler_list_404():
    """
    A request for the tiddlers in a non existent bag gives a 404.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag99/tiddlers',
            method='GET')

    assert response['status'] == '404'

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

    assert response['last-modified'] == 'Fri, 23 May 2008 03:03:00 GMT'
    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert len(content.rstrip().split('\n')) == 1, 'len tiddlers should be 1 is %s' % len(content.rstrip().split('\n'))

def test_get_bags_default():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags',
            method='GET')

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/html; charset=UTF-8', 'response content-type should be text/html;charset=UTF-8 is %s' % response['content-type']
    assert len(content.rstrip().split('\n')) == 32, 'len bags should be 33 is %s' % len(content.rstrip().split('\n'))

def test_get_bags_txt():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags.txt',
            method='GET')

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/plain; charset=UTF-8', 'response content-type should be text/plain; charset=UTF-8 is %s' % response['content-type']
    assert len(content.rstrip().split('\n')) == 30, 'len bags should be 32 is %s' % len(content.rstrip().split('\n'))

def test_get_bags_html():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags.html',
            method='GET')

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/html; charset=UTF-8', 'response content-type should be text/html;charset=UTF-8 is %s' % response['content-type']
    assert len(content.rstrip().split('\n')) == 32, 'len bags should be 33 is %s' % len(content.rstrip().split('\n'))

def test_get_bags_unsupported_neg_format():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags.gif',
            method='GET')

    assert response['status'] == '415', 'response status should be 415 is %s' % response['status']

def test_get_bags_unsupported_recipe_format():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags.jpeg',
            method='GET')

    assert response['status'] == '415', 'response status should be 415 is %s' % response['status']

def test_get_bags_json():
    """
    Fails over to accept header.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags.json',
            method='GET')

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'application/json; charset=UTF-8', \
            'response content-type should be application/json; charset=UTF-8 is %s' % response['content-type']
    info = simplejson.loads(content)
    assert type(info) == list
    assert len(info) == 30

def test_get_bags_unsupported_neg_format_with_accept():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags.gif',
            method='GET', headers={'Accept': 'text/html'})

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/html; charset=UTF-8', 'response content-type should be text/html;charset=UTF-8 is %s' % response['content-type']

def test_get_bag_tiddler_list_empty():
    """
    A request for the tiddlers in a non existent bag gives a 404.
    """

    bag = Bag('bagempty');
    store.put(bag)

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bagempty/tiddlers.txt',
            method='GET')

    assert response['status'] == '200'
    assert content == ''

def test_put_bag():
    """
    PUT a new bag to the server.
    """
    json_string = simplejson.dumps(dict(policy=policy_dict))

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bagpuss',
            method='PUT', headers={'Content-Type': 'application/json'}, body=json_string)
    location = response['location']

    assert response['status'] == '204'
    assert location == 'http://our_test_domain:8001/bags/bagpuss'

    response, content = http.request(location, method='GET',
            headers={'Accept': 'application/json'})

    assert response['status'] == '200'
    assert content == '[]' # empty json list

def test_put_bag_wrong_type():
    """
    PUT a new bag to the server.
    """
    json_string = simplejson.dumps(dict(policy=policy_dict))

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bagpuss',
            method='PUT', headers={'Content-Type': 'text/plain'}, body=json_string)

    assert response['status'] == '415'
