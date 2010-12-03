"""
An HTTP test running. Call http_test with the filename
of a YAML file containing tests and a base_url for the
test server.
"""
import os

import httplib2
import simplejson

from base64 import b64encode
from re import match

from fixtures import muchdata, reset_textstore, _teststore, initialize_app

from tiddlyweb.model.user import User

tests = store = http = None

__all__ = ('http_test', 'test_assert_response', 'test_the_TESTS')

def http_test(test_data, base):
    global tests, store, http, base_url
    base_url = base
    tests = test_data
    initialize_app()
    reset_textstore()
    store = _teststore()
    muchdata(store)

    # we're going to need a user for testing auth stuff
    # so make that now
    user = User('cdent')
    user.set_password('cowpig')
    store.put(user)
    http = httplib2.Http()


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


def test_the_TESTS():
    """
    Run the entire TEST.
    """
    for test_data in tests:
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
    assert response['status'] == '%s' % status, (response, content)

    if headers:
        for header in headers:
            assert response[header] == headers[header]

    if expected:
        for expect in expected:
            assert expect.encode('UTF-8') in content
