

import os

from gabbi.driver import build_tests

from tiddlyweb.web.serve import load_app

from gabbitests import fixtures


TESTS_DIR = 'gabbits'


def load_tests(loader, tests, pattern):
    test_dir = os.path.join(os.path.dirname(__file__), TESTS_DIR)
    return build_tests(test_dir, loader, host=None,
                       intercept=load_app,
                       fixture_module=fixtures)

