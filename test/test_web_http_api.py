"""
Run through the entire API to expound,
expand, explain, etc.

Read the TESTS variable as document of
the capabilities of the API.

If you run this test file by itself, instead
of as a test it will produce a list of test
requests and some associated information.
"""

import os

from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2
import simplejson
import yaml

from base64 import b64encode
from re import match

from fixtures import muchdata, reset_textstore, _teststore

from tiddlyweb.model.user import User

authorization = b64encode('cdent:cowpig')
base_url = 'http://our_test_domain:8001'

def setup_module(module):
    from tiddlyweb.web import serve
    def app_fn():
        return serve.load_app()
    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('our_test_domain', 8001, app_fn)

    reset_textstore()
    module.store = _teststore()
    muchdata(module.store)

    # we're going to need a user for testing auth stuff
    # so make that now
    user = User('cdent')
    user.set_password('cowpig')
    module.store.put(user)

    module.http = httplib2.Http()

def test_assert_response():
    """
    Make sure our assertion tester is valid.
    """
    response = {
            'status': '200',
            'location': 'http://example.com',
            }
    content = 'Hello World\n'
    status = '200'
    headers = {
            'location': 'http://example.com',
            }
    expected = ['Hello']

    assert_response(response, content, status, headers, expected)

EMPTY_TEST = {
        'name': '',
        'desc': '',
        'method': 'GET',
        'url': '',
        'status': '200',
        'request_headers': {},
        'response_headers': {},
        'expected': [],
        'data': '',
        }
TESTS = yaml.load(open('test/httptest.yaml'))

def test_the_TESTS():
    """
    Run the entire TEST.
    """
    for test_data in TESTS:
        test = dict(EMPTY_TEST)
        test.update(test_data)
        yield test['name'], _run_test, test

def _run_test(test):
    full_url = base_url + test['url']
    if test['method'] == 'GET' or test['method'] == 'DELETE':
        response, content = http.request(full_url, method=test['method'], headers=test['request_headers'])
    else:
        response, content = http.request(full_url, method=test['method'], headers=test['request_headers'],
                body=test['data'].encode('UTF-8'))
    assert_response(response, content, test['status'], headers=test['response_headers'], expected=test['expected'])

def assert_response(response, content, status, headers=None, expected=None):
    if response['status'] == '500': print content
    assert response['status'] == '%s' % status

    if headers:
        for header in headers:
            assert response[header] == headers[header]

    if expected:
        for expect in expected:
            assert expect in content

if __name__ == '__main__':
    for test_data in TESTS:
        test = dict(EMPTY_TEST)
        test.update(test_data)
        full_url = base_url + test['url']
        print test['name']
        print '%s %s' % (test['method'], full_url)
        print
