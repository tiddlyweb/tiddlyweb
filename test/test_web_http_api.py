"""
Run through the entire API to expound,
expand, explain, etc.
"""

import yaml

# test_* required to make tests discoverable
from .http_runner import http_test, test_the_TESTS, test_assert_response


def setup_module(module):
    with open('test/httptest.yaml') as yaml_file:
        tests = yaml.load(yaml_file)
        http_test(tests, 'http://our_test_domain:8001')
