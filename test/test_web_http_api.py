"""
Run through the entire API to expound,
expand, explain, etc.

Read the TESTS variable as document of
the capabilities of the API.
"""

from http_runner import *

def setup_module(module):
    http_test('test/httptest.yaml', 'http://our_test_domain:8001')
