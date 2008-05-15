"""
Test that GETting a tiddler in some form.
"""

import sys
sys.path.append('.')

from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2
import simplejson

from fixtures import muchdata

from tiddlyweb.store import Store

text_put_body=u"""modifier: JohnSmith
created: 
modified: 200803030303
tags: tagone

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
    muchdata(module.store)

def test_get_tiddler():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/tiddler8',
            method='GET')

    assert response['status'] == '200', 'response status should be 200'
    assert 'i am tiddler 8' in content, 'tiddler should be correct content, is %s' % content

def test_get_tiddler_revision():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/tiddler8/revisions/1',
            method='GET')

    assert response['status'] == '200', 'response status should be 200'
    assert 'i am tiddler 8' in content, 'tiddler should be correct content, is %s' % content
    assert 'revision="1"' in content

def test_get_missing_tiddler():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/tiddler27',
            method='GET')

    assert response['status'] == '404', 'response status should be 404'

def test_get_missing_tiddler_revision():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/tiddler27/revisions/99',
            method='GET')

    assert response['status'] == '404', 'response status should be 404'

def test_get_tiddler_wiki():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/tiddler8.wiki',
            method='GET')

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/html; charset=UTF-8', 'response content-type should be text/html; chareset=UTF-8 is %s' % response['content-type']
    assert 'i am tiddler 8' in content, 'tiddler should be correct content, is %s' % content

def test_get_tiddler_revision_wiki():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/tiddler8/revisions/1.wiki',
            method='GET')

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/html; charset=UTF-8', 'response content-type should be text/html; chareset=UTF-8 is %s' % response['content-type']
    assert 'i am tiddler 8' in content, 'tiddler should be correct content, is %s' % content
    assert 'revision="1"' in content

def test_put_tiddler_txt():
    http = httplib2.Http()
    encoded_body = text_put_body.encode('UTF-8')
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/TestOne',
            method='PUT', headers={'Content-Type': 'text/plain'}, body=encoded_body)

    assert response['status'] == '204', 'response status should be 204 is %s' % response['status']
    tiddler_url = response['location']
    assert tiddler_url == 'http://our_test_domain:8001/bags/bag0/tiddlers/TestOne', \
            'response location should be http://our_test_domain:8001/bags/bag0/tiddlers/TestOne is %s' \
            % tiddler_url

    response, content = http.request(tiddler_url, headers={'Accept': 'text/plain'})
    content = content.decode('UTF-8')
    assert content.strip().rstrip() == text_put_body.strip().rstrip()#, \
           # 'content should be #%s#, is #%s#' % (content.strip().rstrip(), text_put_body.strip().rstrip())

def test_put_tiddler_txt_no_modified():
    """
    Putting a tiddler with no modifier should make a default.
    """
    http = httplib2.Http()
    encoded_body = text_put_body.encode('UTF-8')
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/TestOne',
            method='PUT', headers={'Content-Type': 'text/plain'}, body='modifier: ArthurDent\n\nTowels')

    assert response['status'] == '204', 'response status should be 204 is %s' % response['status']
    tiddler_url = response['location']
    assert tiddler_url == 'http://our_test_domain:8001/bags/bag0/tiddlers/TestOne', \
            'response location should be http://our_test_domain:8001/bags/bag0/tiddlers/TestOne is %s' \
            % tiddler_url

    response, content = http.request(tiddler_url, headers={'Accept': 'text/plain'})
    content = content.decode('UTF-8')
    assert 'modified: 2' in content

def test_put_tiddler_json():
    http = httplib2.Http()

    json = simplejson.dumps(dict(text='i fight for the users', tags=['tagone','tagtwo'], modifier='', modified='200803030303', created='200803030303'))

    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/TestTwo',
            method='PUT', headers={'Content-Type': 'application/json'}, body=json)

    assert response['status'] == '204', 'response status should be 204 is %s' % response['status']
    tiddler_url = response['location']
    assert tiddler_url == 'http://our_test_domain:8001/bags/bag0/tiddlers/TestTwo', \
            'response location should be http://our_test_domain:8001/bags/bag0/tiddlers/TestTwo is %s' \
            % tiddler_url

    response, content = http.request(tiddler_url, headers={'Accept': 'application/json'})
    info = simplejson.loads(content)
    assert info['title'] == 'TestTwo'
    assert info['text'] == 'i fight for the users'

def test_put_tiddler_json_bad_path():
    """
    / in tiddler title is an unresolved source of some confusion.
    """
    http = httplib2.Http()

    json = simplejson.dumps(dict(text='i fight for the users 2', tags=['tagone','tagtwo'], modifier='', modified='200803030303', created='200803030303'))

    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/..%2F..%2F..%2F..%2FTestThree',
            method='PUT', headers={'Content-Type': 'application/json'}, body=json)

    assert response['status'] == '404', 'response status should be 404 is %s' % response['status']

def test_get_tiddler_via_recipe():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers/tiddler8.json',
            method='GET')

    assert response['status'] == '200'
    tiddler_info = simplejson.loads(content)
    assert tiddler_info['bag'] == 'bag28'

def test_put_tiddler_via_recipe():
    http = httplib2.Http()
    json = simplejson.dumps(dict(text='i fight for the users 2', tags=['tagone','tagtwo'], modifier='', modified='200803030303', created='200803030303'))

    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers/FantasticVoyage',
            method='PUT', headers={'Content-Type': 'application/json'}, body=json)

    assert response['status'] == '204'
    url = response['location']

    reponse, content = http.request(url, method='GET', headers={'Accept': 'application/json'})
    tiddler_dict = simplejson.loads(content)
    assert tiddler_dict['bag'] == 'bag1'

def test_put_tiddler_txt():
    http = httplib2.Http()
    encoded_body = text_put_body.encode('UTF-8')
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/TestOne',
            method='PUT', headers={'Content-Type': 'text/plain'}, body=encoded_body)

    assert response['status'] == '204', 'response status should be 204 is %s' % response['status']
    tiddler_url = response['location']
    assert tiddler_url == 'http://our_test_domain:8001/bags/bag0/tiddlers/TestOne', \
            'response location should be http://our_test_domain:8001/bags/bag0/tiddlers/TestOne is %s' \
            % tiddler_url

    response, content = http.request(tiddler_url, headers={'Accept': 'text/plain'})
    content = content.decode('UTF-8')
    assert content.strip().rstrip() == text_put_body.strip().rstrip()
