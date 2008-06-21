"""
Test the way in which the /challenge URI produces stuff.
"""

import sys
sys.path.append('.')

from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2
import simplejson

from base64 import b64encode

from fixtures import muchdata, reset_textstore
from tiddlyweb.store import Store

def setup_module(module):
    from tiddlyweb.web import serve
    serve.config['auth_systems'].append('not.really.there')
    def app_fn():
        return serve.default_app('our_test_domain', 8001, 'urls.map')
    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('our_test_domain', 8001, app_fn)
    module.store = Store('text')
    reset_textstore()
    muchdata(module.store)

def test_challenge_base():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/challenge', method='GET')

    assert response['status'] == '401'
    assert 'cookie_form' in content

def test_challenge_cookie_form():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/challenge/cookie_form', method='GET')

    assert response['status'] == '200'
    assert '<form' in content

def test_challenge_not_there_in_config():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/challenge/not_there', method='GET')

    assert response['status'] == '404'

def test_challenge_unable_to_import():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/challenge/not.really.there', method='GET')

    print content
    assert response['status'] == '404'
    assert 'Unable to import' in content

def test_redirect_to_challenge():
    _put_policy('bag28', dict(policy=dict(read=['cdent'],write=['cdent'])))

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers/tiddler8',
            method='GET')
    assert response['status'] == '401'
    assert 'cookie_form' in content

def test_simple_cookie_redirect():
    raised = 0
    try:
        http = httplib2.Http()
        response, content = http.request(\
                'http://our_test_domain:8001/challenge/cookie_form?user=cdent&password=cdent&tiddlyweb_redirect=/recipes/long/tiddlers/tiddler8',
                method='GET', redirections=0)
    except httplib2.RedirectLimit, e:
        raised = 1

    assert raised
    assert e.response['status'] == '303'
    headers = {}
    headers['cookie'] = e.response['set-cookie']
    response, content = http.request(e.response['location'], method='GET', headers=headers)
    assert response['status'] == '200'
    assert 'i am tiddler 8' in content

def _put_policy(bag_name, policy_dict):
    json = simplejson.dumps(policy_dict)

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/%s' % bag_name,
            method='PUT', headers={'Content-Type': 'application/json'}, body=json)
    assert response['status'] == '204'