"""
Run through the entire API to expound,
expand, explain, etc.

Read the TESTS variable as document of
the capabilities of the API.
"""

import yaml

from http_runner import *

def setup_module(module):
    tests = yaml.load(open('test/httptest.yaml'))
    http_test(tests, 'http://our_test_domain:8001')
