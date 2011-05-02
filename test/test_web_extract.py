"""
Test the way in which the /challenge URI produces stuff.

XXX This test file appears to have never been completed.
"""


import httplib2
import simplejson

from base64 import b64encode

from fixtures import muchdata, reset_textstore, _teststore, initialize_app

from tiddlyweb.config import config
from tiddlyweb.model.user import User

def init(config):
    config['selector'].add('/current_user', GET=user)

def user(environ, start_response):
    username = environ['tiddlyweb.usersign']['name']
    start_response('200 OK', [
        ('Content-Type', 'text/plain')])
    return ["%s\n" % username]

def setup_module(module):
    config['system_plugins'].append('test.test_web_extract')
    initialize_app()
    reset_textstore()
    module.store = _teststore()
    user = User('cow')
    user.set_password('pig')
    module.store.put(user)

def teardown_module(module):
    config['extractors'].pop()

def test_extractor_not_there_in_config():
    config['extractors'].append('saliva')
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/', method='GET')

    assert response['status'] == '500'
    assert 'ImportError' in content
    config['extractors'].remove('saliva')

def test_guest_extract():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/current_user', method='GET')

    assert response['status'] == '200'
    assert 'GUEST' in content

def test_user_extract():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/current_user', method='GET',
            headers={'Authorization': 'Basic %s' % b64encode('cow:pig')})
    assert response['status'] == '200'
    assert 'cow' in content

def test_user_extract_bad_pass():
    """User gets their password wrong, user is GUEST"""
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/current_user', method='GET',
            headers={'Authorization': 'Basic %s' % b64encode('cow:pog')})
    assert response['status'] == '200'
    assert 'GUEST' in content

def test_user_extract_no_user():
    """User doesn't exist, user is GUEST"""
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/current_user', method='GET',
            headers={'Authorization': 'Basic %s' % b64encode('ciw:pig')})
    assert response['status'] == '200'
    assert 'GUEST' in content

def test_user_extract_bogus_data():
    """User doesn't exist, user is GUEST"""
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/current_user', method='GET',
            headers={'Authorization': 'Basic %s' % b64encode(':')})
    assert response['status'] == '200'
    assert 'GUEST' in content

def test_bad_cookie():
    """confirm a bad cookie results in an error"""
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/current_user', method='GET',
            headers={'Cookie': 'foo(bar)bar="monkey"'})
    assert response['status'] == '400'
    assert 'Illegal key value' in content

def test_malformed_tiddlyweb_cookie():
    """confirm a malformed user cookie results in GUEST"""
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/current_user', method='GET',
            headers={'Cookie': 'tiddlyweb_user="cdent.tumblr.com"'})
    assert response['status'] == '200', content
    assert 'GUEST' in content
