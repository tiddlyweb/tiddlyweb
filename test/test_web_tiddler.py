"""
Test that GETting a tiddler in some form.
"""

import os

import py.test

import httplib2
import simplejson

from base64 import b64encode
from re import match

from fixtures import muchdata, reset_textstore, _teststore, initialize_app

import tiddlyweb.stores.text

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.user import User
from tiddlyweb.util import sha
from tiddlyweb.web.util import http_date_from_timestamp

authorization = b64encode('cdent:cowpig')
bad_authorization = b64encode('cdent:cdent')
no_user_authorization = b64encode('foop:foop')

text_put_body=u"""modifier: JohnSmith
created: 
modified: 200803030303
tags: tagone

Hello, I'm John Smith \xbb and I have something to sell.
"""

def setup_module(module):
    initialize_app()
    reset_textstore()
    module.store = _teststore()
    muchdata(module.store)

    user = User('cdent')
    user.set_password('cowpig')
    module.store.put(user)

    try:
        os.mkdir('.test_cache')
    except OSError:
        pass # we don't care if it already exists

def test_get_tiddler():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/tiddler8',
            method='GET')

    assert response['status'] == '200', content
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

def test_get_tiddler_missing_revision():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/tiddler8/revisions/99',
            method='GET')

    assert response['status'] == '404'

def test_put_tiddler_txt():
    http = httplib2.Http()
    encoded_body = text_put_body.encode('utf-8')
    funkity_encoding = text_put_body.encode('latin1')
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/TestOne',
            method='PUT', headers={'Content-Type': 'text/plain'}, body=encoded_body)
    tiddler_url = response['location']

    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/TestOne',
            method='PUT', headers={'Content-Type': 'text/plain'}, body=funkity_encoding)

    assert response['status'] == '400', content
    assert 'unable to decode tiddler' in content

    assert tiddler_url == 'http://our_test_domain:8001/bags/bag0/tiddlers/TestOne', \
            'response location should be http://our_test_domain:8001/bags/bag0/tiddlers/TestOne is %s' \
            % tiddler_url

    response, content = http.request(tiddler_url, headers={'Accept': 'text/plain'})
    content = content.decode('utf-8')
    contents = content.strip().rstrip().split('\n')
    texts = text_put_body.strip().rstrip().split('\n')
    assert contents[-1] == texts[-1] # text
    assert contents[-3] == texts[-3] # tags

def test_put_tiddler_txt_no_modified():
    """
    Putting a tiddler with no modifier should make a default.
    """
    http = httplib2.Http()
    encoded_body = text_put_body.encode('utf-8')
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/TestOne',
            method='PUT', headers={'Content-Type': 'text/plain'}, body='modifier: ArthurDent\n\nTowels')

    assert response['status'] == '204', 'response status should be 204 is %s' % response['status']
    tiddler_url = response['location']
    assert tiddler_url == 'http://our_test_domain:8001/bags/bag0/tiddlers/TestOne', \
            'response location should be http://our_test_domain:8001/bags/bag0/tiddlers/TestOne is %s' \
            % tiddler_url

    response, content = http.request(tiddler_url, headers={'Accept': 'text/plain'})
    content = content.decode('utf-8')
    assert 'modified: 2' in content

def test_put_tiddler_json():
    http = httplib2.Http()

    json = simplejson.dumps(dict(text='i fight for the users',
        tags=['tagone','tagtwo'], modifier=''))

    response, content = http.request(
            'http://our_test_domain:8001/bags/bag0/tiddlers/TestTwo',
            method='PUT',
            headers={'Content-Type': 'application/json',
                'Content-Length': '0'},
            body='')
    assert response['status'] == '400'
    assert 'unable to make json into' in content

    response, content = http.request(
            'http://our_test_domain:8001/bags/bag0/tiddlers/TestTwo',
            method='PUT',
            headers={'Content-Type': 'application/json'},
            body='{"text": "}')
    assert response['status'] == '400'
    assert 'unable to make json into' in content

    response, content = http.request(
            'http://our_test_domain:8001/bags/bag0/tiddlers/TestTwo',
            method='PUT', headers={'Content-Type': 'application/json'},
            body=json)

    assert response['status'] == '204'
    tiddler_url = response['location']
    assert (tiddler_url ==
            'http://our_test_domain:8001/bags/bag0/tiddlers/TestTwo')

    response, content = http.request(tiddler_url,
            headers={'Accept': 'application/json'})
    info = simplejson.loads(content)
    now_time = http_date_from_timestamp('')
    assert response['last-modified'].split(':', 1)[0] == now_time.split(':', 1)[0]
    assert info['title'] == 'TestTwo'
    assert info['text'] == 'i fight for the users'
    assert info['uri'] == tiddler_url

def test_put_tiddler_json_with_slash():
    http = httplib2.Http()

    json = simplejson.dumps(dict(text='i fight for the users', tags=['tagone','tagtwo'], modifier='', modified='200805230303', created='200803030303'))

    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/Test%2FSlash',
            method='PUT', headers={'Content-Type': 'application/json'}, body=json)

    assert response['status'] == '204', 'response status should be 204 is %s' % response['status']
    assert response['location'] == 'http://our_test_domain:8001/bags/bag0/tiddlers/Test%2FSlash'


def test_put_tiddler_html_in_json():
    http = httplib2.Http()

    json = simplejson.dumps(dict(
        text='<html><head><title>HI</title><body><h1>HI</h1></body></html>'))

    response, content = http.request(
            'http://our_test_domain:8001/bags/bag0/tiddlers/TestHTML',
            method='PUT', headers={'Content-Type': 'application/json'},
            body=json)

    assert response['status'] == '204'
    location = response['location']

    response, content = http.request(location,
            headers={'User-Agent': 'Mozilla'})
    assert response['status'] == '200'
    assert 'text/html' in response['content-type']
    # Title should not be there
    assert '<title>HI</title>' not in content
    assert '<title>TiddlyWeb - TestHTML</title>' in content
    assert '&lt;h1&gt;HI&lt;/h1&gt;' in content

    json = simplejson.dumps(dict(
        text='<html><head><title>HI</title><body><h1>HI</h1></body></html>',
        type='text/html'))

    response, content = http.request(
            'http://our_test_domain:8001/bags/bag0/tiddlers/TestHTML',
            method='PUT', headers={'Content-Type': 'application/json',
                'User-Agent': 'Mozilla'},
            body=json)

    assert response['status'] == '204'
    location = response['location']

    response, content = http.request(location)
    assert response['status'] == '200'
    assert 'text/html' in response['content-type']
    # Title should not be wrapping in tiddly info
    assert '<title>HI</title>' in content
    assert '<h1>HI</h1>' in content


def test_put_tiddler_json_bad_path():
    """
    / in tiddler title is an unresolved source of some confusion.
    """
    http = httplib2.Http()

    if type(store.storage) != tiddlyweb.stores.text.Store:
        py.test.skip('skipping this test for non-text store')

    json = simplejson.dumps(dict(text='i fight for the users 2', tags=['tagone','tagtwo'], modifier='', modified='200803030303', created='200803030303'))

    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/..%2F..%2F..%2F..%2FTestThree',
            method='PUT', headers={'Content-Type': 'application/json'}, body=json)

    assert response['status'] == '404', 'response status should be 404 is %s' % response['status']

def test_put_tiddler_json_no_bag():
    http = httplib2.Http()

    json = simplejson.dumps(dict(text='i fight for the users 2', tags=['tagone','tagtwo'], modifier='', modified='200803030303', created='200803030303'))

    response, content = http.request('http://our_test_domain:8001/bags/nobagheremaam/tiddlers/SomeKindOTiddler',
            method='PUT', headers={'Content-Type': 'application/json'}, body=json)

    assert response['status'] == '409'
    assert 'There is no bag named: nobagheremaam' in content

def test_get_tiddler_via_recipe():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers/tiddler8.json',
            method='GET')

    assert response['status'] == '200', content
    tiddler_info = simplejson.loads(content)
    assert tiddler_info['bag'] == 'bag28'

def test_get_tiddler_etag_recipe():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers/tiddler8.json',
            method='GET')

    assert response['status'] == '200'
    assert response['etag'].startswith('"bag28/tiddler8/1:')
    tiddler_info = simplejson.loads(content)
    assert tiddler_info['bag'] == 'bag28'

def test_get_tiddler_etag_bag():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag28/tiddlers/tiddler8.json',
            method='GET')

    assert response['status'] == '200'
    assert response['etag'].startswith('"bag28/tiddler8/1:')
    tiddler_info = simplejson.loads(content)
    assert tiddler_info['bag'] == 'bag28'

def test_get_tiddler_manual_cache():
    [os.unlink('.test_cache/%s' % x) for x in os.listdir('.test_cache')]
    http = httplib2.Http('.test_cache')
    tiddler = Tiddler('cached', 'bag28')
    tiddler.text = 'hi!'
    tiddler.fields['_cache-max-age'] = 3000
    store.put(tiddler)

    response, content = http.request(
            'http://our_test_domain:8001/bags/bag28/tiddlers/cached')
    assert not response.fromcache
    assert response['status'] == '200'
    assert response['cache-control'] == 'max-age=3000'
    assert 'text/html' in response['content-type']
    htmletag = response['etag']

    response, content = http.request(
            'http://our_test_domain:8001/bags/bag28/tiddlers/cached',
            headers={'Accept': 'text/plain'})
    assert not response.fromcache
    assert response['status'] == '200'
    assert response['cache-control'] == 'max-age=3000'
    assert 'text/plain' in response['content-type']
    
    response, content = http.request(
            'http://our_test_domain:8001/bags/bag28/tiddlers/cached')
    # this one does not cache because we Vary on Accept
    assert not response.fromcache
    assert response['status'] == '200'
    assert response['etag'] == htmletag

    response, content = http.request(
            'http://our_test_domain:8001/bags/bag28/tiddlers/cached')
    assert response.fromcache
    assert response['status'] == '304'
    assert 'text/html' in response['content-type']
    assert response['etag'] == htmletag

    tiddler = Tiddler('notcached', 'bag28')
    tiddler.text = 'hi!'
    tiddler.fields['_cache-max-age'] = 'salami'
    store.put(tiddler)
    response, content = http.request(
            'http://our_test_domain:8001/bags/bag28/tiddlers/notcached')
    assert not response.fromcache
    assert response['status'] == '200'
    assert response['cache-control'] == 'no-cache'
    assert 'max-age' not in response['cache-control']
    assert 'text/html' in response['content-type']


def test_get_tiddler_cached():
    [os.unlink('.test_cache/%s' % x) for x in os.listdir('.test_cache')]
    http = httplib2.Http('.test_cache')
    response, content = http.request('http://our_test_domain:8001/bags/bag28/tiddlers/tiddler8',
            headers={'Accept': 'application/json'},
            method='GET')
    assert not response.fromcache
    assert response['status'] == '200'
    assert response['etag'].startswith('"bag28/tiddler8/1:')

    response, content = http.request('http://our_test_domain:8001/bags/bag28/tiddlers/tiddler8',
            headers={'Accept': 'application/json'},
            method='GET')
    assert response.fromcache
    assert response['status'] == '304'
    assert response['etag'].startswith('"bag28/tiddler8/1:')
    
    response, content = http.request('http://our_test_domain:8001/bags/bag28/tiddlers/tiddler8',
            headers={'Accept': 'text/html'},
            method='GET')
    assert response['etag'].startswith('"bag28/tiddler8/1:')
    assert not response.fromcache
    assert response['status'] == '200'

    response, content = http.request('http://our_test_domain:8001/bags/bag28/tiddlers/tiddler8',
            headers={'Accept': 'application/json'},
            method='GET')
    assert not response.fromcache
    assert response['status'] == '200'
    assert response['etag'].startswith('"bag28/tiddler8/1:')

    response, content = http.request('http://our_test_domain:8001/bags/bag28/tiddlers/tiddler8',
            headers={'Accept': 'application/json'},
            method='GET')
    assert response.fromcache
    assert response['status'] == '304'
    assert response['etag'].startswith('"bag28/tiddler8/1:')

def test_put_tiddler_recipe_with_filter():
    recipe = Recipe('recipe1')
    bag1 = Bag('bag1')
    bag2 = Bag('bag2')
    recipe.set_recipe([('bag1', ''), ('bag2', 'select=tag:foo')])
    store.put(bag1)
    store.put(bag2)
    store.put(recipe)

    tiddler_json_one =simplejson.dumps(dict(text='hello', tags=[]))
    tiddler_json_two =simplejson.dumps(dict(text='hello', tags=['foo']))

    http = httplib2.Http()
    response, content = http.request(
            'http://our_test_domain:8001/recipes/recipe1/tiddlers/tiddler_one',
            headers={'Content-Type': 'application/json'},
            method='PUT',
            body=tiddler_json_one)
    assert response['status'] == '204'
    assert 'bag1' in response['etag']

    response, content = http.request(
            'http://our_test_domain:8001/recipes/recipe1/tiddlers/tiddler_two',
            headers={'Content-Type': 'application/json'},
            method='PUT',
            body=tiddler_json_two)
    assert response['status'] == '204'
    assert 'bag2' in response['etag']

    tiddler = Tiddler('tiddler_three', 'bag2')
    tiddler.tags = ['foo']
    store.put(tiddler)

    response, content = http.request(
            'http://our_test_domain:8001/recipes/recipe1/tiddlers/tiddler_two',
            headers={'Content-Type': 'application/json'},
            method='PUT',
            body=tiddler_json_two)
    assert response['status'] == '204'
    assert 'bag2' in response['etag']





def test_put_tiddler_cache_fakey():
    [os.unlink('.test_cache/%s' % x) for x in os.listdir('.test_cache')]
    http_caching = httplib2.Http('.test_cache')
    http = httplib2.Http()

    json = simplejson.dumps(dict(text='i fight for the users 2', tags=['tagone','tagtwo'], modifier='', modified='200803030303', created='200803030303'))

    response, content = http_caching.request('http://our_test_domain:8001/recipes/long/tiddlers/CashForCache',
            method='PUT', headers={'Content-Type': 'application/json'}, body=json)
    assert response['status'] == '204'
    assert response['etag'].startswith('"bag1/CashForCache/1:')

    response, content = http_caching.request('http://our_test_domain:8001/recipes/long/tiddlers/CashForCache',
            method='GET', headers={'Accept': 'application/json'})
    assert response['status'] == '200'
    assert response['etag'].startswith('"bag1/CashForCache/1:')

    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers/CashForCache',
            method='PUT', headers={'Content-Type': 'application/json'}, body=json)
    assert response['status'] == '204'
    assert response['etag'].startswith('"bag1/CashForCache/2:')

    response, content = http_caching.request('http://our_test_domain:8001/recipes/long/tiddlers/CashForCache',
            method='PUT', headers={'Content-Type': 'application/json'}, body=json)
    assert response['status'] == '412'

def test_put_tiddler_via_recipe():
    http = httplib2.Http()
    json = simplejson.dumps(dict(text='i fight for the users 2', tags=['tagone','tagtwo'], modifier='', modified='200803030303', created='200803030303'))

    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers/FantasticVoyage',
            method='PUT', headers={'Content-Type': 'application/json'}, body=json)

    assert response['status'] == '204'
    assert response['etag'].startswith('"bag1/FantasticVoyage/1:')
    url = response['location']

    reponse, content = http.request(url, method='GET', headers={'Accept': 'application/json'})
    tiddler_dict = simplejson.loads(content)
    assert tiddler_dict['bag'] == 'bag1'
    assert response['etag'].startswith('"bag1/FantasticVoyage/1:')

def test_slash_in_etag():
    http = httplib2.Http()

    json = simplejson.dumps(dict(text='i fight for the users', tags=['tagone','tagtwo'], modifier='', modified='200805230303', created='200803030303'))

    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/Test%2FTwo',
            method='PUT', headers={'Content-Type': 'application/json'}, body=json)
    assert response['status'] == '204'

    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/Test%2FTwo',
            method='PUT', headers={'Content-Type': 'application/json', 'If-Match': '"bag0/Test%2FTwo/1"'}, body=json)
    assert response['status'] == '204'

    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/Test%2FTwo',
            method='PUT', headers={'Content-Type': 'application/json', 'If-Match': '"bag0/Test/Two/2"'}, body=json)
    assert response['status'] == '412'

    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/Test%2FTwo',
            method='PUT', headers={'Content-Type': 'application/json', 'If-Match': '"bag0/Test%2FTwo/2"'}, body=json)
    assert response['status'] == '204'

def test_paren_in_etag():
    http = httplib2.Http()

    json = simplejson.dumps(dict(text='i fight for the users', tags=['tagone','tagtwo'], modifier='', modified='200805230303', created='200803030303'))

    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/Test(Two)',
            method='PUT', headers={'Content-Type': 'application/json'}, body=json)
    assert response['status'] == '204'

    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/Test(Two)',
            method='PUT', headers={'Content-Type': 'application/json', 'If-Match': '"bag0/Test(Two)/1"'}, body=json)
    assert response['status'] == '204'

    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/Test(Two)',
            method='PUT', headers={'Content-Type': 'application/json', 'If-Match': '"bag0/Test%28Two%29/2"'}, body=json)
    assert response['status'] == '412'

    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/Test(Two)',
            method='PUT', headers={'Content-Type': 'application/json', 'If-Match': '"bag0/Test(Two)/2"'}, body=json)
    assert response['status'] == '204'

def test_get_tiddler_text_created():
    """
    Make sure the tiddler comes back to us as we expect.
    In the process confirm that Accept header processing is working
    as expect, by wanting xml (which we don't do), more than text/plain,
    which we do.
    """
    http = httplib2.Http()
    tiddler_url = 'http://our_test_domain:8001/bags/bag0/tiddlers/TestOne'
    response, content = http.request(tiddler_url, headers={'Accept': 'text/xml; q=1, text/plain'})

    content = content.decode('utf-8')
    contents = content.strip().rstrip().split('\n')
    texts = text_put_body.strip().rstrip().split('\n')
    assert contents[-1] == u'Towels' # text
    assert contents[-3] == u'tags: ' # tags
    assert match('created: \d{12}', contents[1])

def test_tiddler_bag_constraints():
    encoded_body = text_put_body.encode('utf-8')
    http = httplib2.Http()
    _put_policy('unreadable', dict(policy=dict(manage=['cdent'],read=['NONE'],write=['NONE'],create=['NONE'])))

    # try to create a tiddler and fail
    response, content = http.request('http://our_test_domain:8001/bags/unreadable/tiddlers/WroteOne',
            method='PUT', headers={'Content-Type': 'text/plain', 'Authorization': 'Basic %s' % authorization},
            body=encoded_body)
    assert response['status'] == '403'
    assert 'may not create' in content

    # create and succeed
    _put_policy('unreadable', dict(policy=dict(manage=['cdent'],read=['NONE'],write=['NONE'],create=['cdent'])))
    response, content = http.request('http://our_test_domain:8001/bags/unreadable/tiddlers/WroteOne',
            method='PUT', headers={'Content-Type': 'text/plain', 'Authorization': 'Basic %s' % authorization},
            body=encoded_body)
    assert response['status'] == '204'

    # fail when bad auth format
    _put_policy('unreadable', dict(policy=dict(manage=['cdent'],read=['NONE'],write=['NONE'],create=['cdent'])))
    response, content = http.request('http://our_test_domain:8001/bags/unreadable/tiddlers/WroteOne',
            method='PUT', headers={'Content-Type': 'text/plain', 'Authorization': '%s' % authorization},
            body=encoded_body)
    assert response['status'] == '403'

    # fail when bad auth info
    _put_policy('unreadable', dict(policy=dict(manage=['cdent'],read=['NONE'],write=['NONE'],create=['cdent'])))
    response, content = http.request('http://our_test_domain:8001/bags/unreadable/tiddlers/WroteOne',
            method='PUT', headers={'Content-Type': 'text/plain', 'Authorization': 'Basic %s' % bad_authorization},
            body=encoded_body)
    assert response['status'] == '403'

    # fail when bad user info
    _put_policy('unreadable', dict(policy=dict(manage=['cdent'],read=['NONE'],write=['NONE'],create=['cdent'])))
    response, content = http.request('http://our_test_domain:8001/bags/unreadable/tiddlers/WroteOne',
            method='PUT', headers={'Content-Type': 'text/plain', 'Authorization': 'Basic %s' % no_user_authorization},
            body=encoded_body)
    assert response['status'] == '403'

    # write and fail
    response, content = http.request('http://our_test_domain:8001/bags/unreadable/tiddlers/WroteOne',
            method='PUT', headers={'Content-Type': 'text/plain', 'Authorization': 'Basic %s' % authorization},
            body=encoded_body)
    assert response['status'] == '403'
    assert 'may not write' in content

    # write and succeed
    _put_policy('unreadable', dict(policy=dict(manage=['cdent'],read=['NONE'],write=['cdent'],create=['NONE'])))
    response, content = http.request('http://our_test_domain:8001/bags/unreadable/tiddlers/WroteOne',
            method='PUT', headers={'Content-Type': 'text/plain', 'Authorization': 'Basic %s' % authorization},
            body=encoded_body)
    assert response['status'] == '204'

    # read and fail
    response, content = http.request('http://our_test_domain:8001/bags/unreadable/tiddlers/WroteOne',
            method='GET', headers={'Accept': 'text/plain', 'Authorization': 'Basic %s' % authorization})
    assert response['status'] == '403'
    assert 'may not read' in content

    # update the policy so we can read and GET the thing
    _put_policy('unreadable', dict(policy=dict(manage=['cdent'],read=['cdent'],write=['NONE'],delete=['NONE'])))
    response, content = http.request('http://our_test_domain:8001/bags/unreadable/tiddlers/WroteOne',
            method='GET', headers={'Accept': 'text/plain', 'Authorization': 'Basic %s' % authorization})
    assert response['status'] == '200'
    assert 'John Smith' in content

def test_get_tiddler_via_recipe_with_perms():

    _put_policy('bag28', dict(policy=dict(manage=['cdent'],read=['NONE'],write=['NONE'])))
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers/tiddler8.json',
            method='GET')
    assert response['status'] == '403'
    assert 'may not read' in content

    _put_policy('bag28', dict(policy=dict(manage=['cdent'],read=['cdent'],write=['NONE'])))
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers/tiddler8.json',
            headers=dict(Authorization='Basic %s' % authorization), method='GET')
    assert response['status'] == '200'

    tiddler_info = simplejson.loads(content)
    assert tiddler_info['bag'] == 'bag28'

    encoded_body = text_put_body.encode('utf-8')
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers/tiddler8',
            method='PUT', headers={'Content-Type': 'text/plain', 'Authorization': 'Basic %s' % authorization},
            body=encoded_body)
    assert response['status'] == '403'
    assert 'may not write' in content

    _put_policy('bag28', dict(policy=dict(manage=['cdent'],read=['cdent'],write=['nancy'])))
    encoded_body = text_put_body.encode('utf-8')
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers/tiddler8',
            method='PUT', headers={'Content-Type': 'text/plain', 'Authorization': 'Basic %s' % authorization},
            body=encoded_body)
    assert response['status'] == '403'

    _put_policy('bag28', dict(policy=dict(manage=['cdent'],read=['cdent'],write=['cdent'])))
    encoded_body = text_put_body.encode('utf-8')
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers/tiddler8',
            method='PUT', headers={'Content-Type': 'text/plain'},
            body=encoded_body)
    # when we PUT without permission there's no good way to handle auth
    # so we just forbid.
    assert response['status'] == '403'

def test_delete_tiddler_in_recipe():
    """disabled in tiddlyweb 1.1"""
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers/tiddler8',
            method='DELETE')
    assert response['status'] == '405'


def test_delete_tiddler_in_bag():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/TestOne',
            method='DELETE')
    assert response['status'] == '204'

    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/TestOne',
            method='DELETE')
    assert response['status'] == '404'


def test_delete_tiddler_etag():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag5/tiddlers/tiddler0',
            method='DELETE', headers={'If-Match': '"bag5/tiddler0/9"'})
    assert response['status'] == '412'

    response, content = http.request('http://our_test_domain:8001/bags/bag5/tiddlers/tiddler0',
            method='DELETE', headers={'If-Match': '"bag5/tiddler0/1"'})
    assert response['status'] == '204'

    response, content = http.request('http://our_test_domain:8001/bags/bag5/tiddlers/tiddler0',
            method='DELETE')
    assert response['status'] == '404'


def test_delete_tiddler_in_bag_perms():
    _put_policy('bag0', dict(policy=dict(manage=['cdent'],read=['cdent'],write=['cdent'],delete=['cdent'])))
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/tiddler0',
            method='DELETE')
    assert response['status'] == '403'

    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/tiddler0',
            method='DELETE', headers={'Authorization': 'Basic %s' % authorization})
    assert response['status'] == '204'

    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/tiddler0',
            method='DELETE', headers={'Authorization': 'Basic %s' % authorization})
    assert response['status'] == '404'

def test_tiddler_no_recipe():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/short/tiddlers/tiddler8',
            method='GET')
    assert response['status'] == '404'

def test_binary_text_tiddler():
    text = 'alert("hello");'
    http = httplib2.Http()
    response, content = http.request(
            'http://our_test_domain:8001/recipes/long/tiddlers/jquery.min.js',
            method='PUT', headers={'Content-Type': 'text/javascript'},
            body=text)
    assert response['status'] == '204', content

    response, content = http.request(
            'http://our_test_domain:8001/recipes/long/tiddlers/jquery.min.js',
            method='GET')
    assert response['status'] == '200'
    assert content == text

    response, content = http.request(
            'http://our_test_domain:8001/recipes/long/tiddlers/jquery.min.js',
            headers={'Accept': 'application/json'},
            method='GET')
    assert response['status'] == '200'
    assert '"text"' in content

    response, content = http.request(
            'http://our_test_domain:8001/recipes/long/tiddlers/jquery.min.js.json',
            method='GET')
    assert response['status'] == '200'
    assert '"text"' in content

def test_binary_tiddler():
    image = file('test/peermore.png', 'rb')
    image_content = image.read()
    image.close()

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers/peermorepng',
            method='PUT', headers={'Content-Type': 'image/png'},
            body=image_content)

    assert response['status'] == '204'

    response, content = http.request(
            'http://our_test_domain:8001/recipes/long/tiddlers/peermore.png',
            method='PUT', headers={'Content-Type': 'image/png'},
            body=image_content)

    assert response['status'] == '204'

    response, content = http.request(
            'http://our_test_domain:8001/recipes/long/tiddlers/peermore.foo.png',
            method='PUT', headers={'Content-Type': 'image/png'},
            body=image_content)

    assert response['status'] == '204'

    response, content = http.request(
            'http://our_test_domain:8001/recipes/long/tiddlers/peermore.foo.bar',
            method='PUT', headers={'Content-Type': 'image/png'},
            body=image_content)

    assert response['status'] == '204'

    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers/peermorepng',
            method='GET')
    assert response['status'] == '200'
    assert response['content-type'] == 'image/png'

    # make sure a binary tiddler in a recipe doesn't cause a select
    # filter to blow up
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers?select=text:hello',
            method='GET')
    assert response['status'] == '200'

    response, content = http.request(
            'http://our_test_domain:8001/recipes/long/tiddlers/peermorepng.json',
            method='GET')
    assert response['status'] == '200'
    assert response['content-type'] == 'application/json; charset=UTF-8'

    response, content = http.request(
            'http://our_test_domain:8001/recipes/long/tiddlers/peermorepng',
            headers={'Accept': 'application/json'},
            method='GET')
    assert response['status'] == '200'
    assert response['content-type'] == 'application/json; charset=UTF-8'

    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers/peermore.png',
            method='GET')
    assert response['status'] == '200'
    assert response['content-type'] == 'image/png'

    response, content = http.request(
            'http://our_test_domain:8001/recipes/long/tiddlers/peermore.png.json',
            method='GET')
    assert response['status'] == '200'
    assert response['content-type'] == 'application/json; charset=UTF-8'

    response, content = http.request(
            'http://our_test_domain:8001/recipes/long/tiddlers/peermore.png',
            headers={'Accept': 'application/json'},
            method='GET')
    assert response['status'] == '200'
    assert response['content-type'] == 'application/json; charset=UTF-8'

    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers/peermore.foo.png',
            method='GET')
    assert response['status'] == '200'
    assert response['content-type'] == 'image/png'

    response, content = http.request(
            'http://our_test_domain:8001/recipes/long/tiddlers/peermore.foo.png.json',
            method='GET')
    assert response['status'] == '200'
    assert response['content-type'] == 'application/json; charset=UTF-8'

    response, content = http.request(
            'http://our_test_domain:8001/recipes/long/tiddlers/peermore.foo.png',
            headers={'Accept': 'application/json'},
            method='GET')
    assert response['status'] == '200'
    assert response['content-type'] == 'application/json; charset=UTF-8'

    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers/peermore.foo.bar',
            method='GET')
    assert response['status'] == '200'
    assert response['content-type'] == 'image/png'

    response, content = http.request(
            'http://our_test_domain:8001/recipes/long/tiddlers/peermore.foo.bar.json',
            method='GET')
    assert response['status'] == '200'
    assert response['content-type'] == 'application/json; charset=UTF-8'

    response, content = http.request(
            'http://our_test_domain:8001/recipes/long/tiddlers/peermore.foo.bar',
            headers={'Accept': 'application/json'},
            method='GET')
    assert response['status'] == '200'
    assert response['content-type'] == 'application/json; charset=UTF-8'

def test_put_json_pseudo_binary():
    http = httplib2.Http()
    json_internal = simplejson.dumps(dict(alpha='car', beta='zoom'))
    json_external = simplejson.dumps(dict(text=json_internal,
        type='application/json'))

    response, content = http.request(
            'http://our_test_domain:8001/bags/bag5/tiddlers/intjson',
            method='PUT',
            body=json_external,
            headers={'Content-Type': 'application/json'})

    assert response['status'] == '204', content

    response, content = http.request(
            'http://our_test_domain:8001/bags/bag5/tiddlers/intjson.json')

    assert response['status'] == '200', content
    assert content == json_internal

def test_bad_uri_encoding():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag5/tiddlers/\x8a\xfa\x91\xd2\x96{\x93y\x98A\xe3\x94\x8c\x80\x92\xf1\x8f\xa1')
    assert response['status'] == '400', content
    assert "codec can't" in content

def test_tiddler_put_create():
    http = httplib2.Http()
    tiddler_data = simplejson.dumps(dict(text='hello'))
    response, content = http.request('http://our_test_domain:8001/bags/bag5/tiddlers/hellotiddler', method='PUT', headers={'If-Match': '"monkeypetard"'})
    # no body raises 400
    assert response['status'] == '400'

    response, content = http.request('http://our_test_domain:8001/bags/bag5/tiddlers/hellotiddler', method='PUT', headers={'If-Match': '"monkeypetard"'}, body=tiddler_data)
    # no content type raises 400
    assert response['status'] == '400'

    response, content = http.request('http://our_test_domain:8001/bags/bag5/tiddlers/hellotiddler', method='PUT', headers={'Content-Type': 'application/json', 'If-Match': '"monkeypetard"'}, body=tiddler_data)
    # Bad form ETag causes 412 on create
    assert response['status'] == '412'

    response, content = http.request('http://our_test_domain:8001/bags/bag5/tiddlers/hellotiddler', method='PUT', headers={'Content-Type': 'application/json', 'If-Match': '"bag5/hellotiddler/99"'}, body=tiddler_data)
    # Bad form ETag causes 412 on create
    assert response['status'] == '412'

    response, content = http.request('http://our_test_domain:8001/bags/bag5/tiddlers/hellotiddler', method='PUT', headers={'Content-Type': 'application/json'}, body=tiddler_data)
    # No ETag we get 204
    assert response['status'] == '204'

    response, content = http.request('http://our_test_domain:8001/bags/bag5/tiddlers/hellotiddler2', method='PUT', headers={'Content-Type': 'application/json', 'If-Match': '"bag5/hellotiddler2/0"'}, body=tiddler_data)
    # Correct ETag we get 204
    assert response['status'] == '204'

    response, content = http.request('http://our_test_domain:8001/bags/bag5/tiddlers/hellotiddler2', method='PUT', headers={'Content-Type': 'application/json', 'If-Match': '"bag5/hellotiddler2/1"'}, body=tiddler_data)
    # Correct ETag we get 204
    assert response['status'] == '204'

    response, content = http.request('http://our_test_domain:8001/bags/bag5/tiddlers/hellotiddler2', method='PUT', headers={'Content-Type': 'application/json', 'If-Match': '"bag5/hellotiddler2/2:application/heartattack"'}, body=tiddler_data)
    # Correct ETag we get 204
    assert response['status'] == '204'

def _put_policy(bag_name, policy_dict):
    json = simplejson.dumps(policy_dict)

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/%s' % bag_name,
            method='PUT', headers={'Content-Type': 'application/json', 'Authorization': 'Basic %s' % authorization},
            body=json)
    assert response['status'] == '204'
