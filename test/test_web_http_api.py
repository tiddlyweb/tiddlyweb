"""
Run through the entire API to expound,
expand, explain, etc.
"""

import yaml
# test_* required to make tests discoverable
from .http_runner import generate_tests, test_generic, http_test


def setup_module(module):
    http_test()


def pytest_generate_tests(metafunc):
    if metafunc.function == test_generic:
        data_file = 'test/httptest.yaml'
        base_url = 'http://our_test_domain:8001'
        with open(data_file) as yaml_file:
            tests = yaml.load(yaml_file)
        data_list, ids = generate_tests(tests, base_url)
        metafunc.parametrize("test, full_url", argvalues=data_list, ids=ids)
