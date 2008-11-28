"""
Test the manager a little bit.
"""

import os
import sys
import StringIO

from tiddlyweb.manage import handle
from fixtures import reset_textstore


def setup_module(module):
    module.savedout = sys.stdout
    module.output = StringIO.StringIO()
    sys.stdout = output

def teardown_module(module):
    content = module.output.getvalue()
    sys.stdout = module.savedout

def test_help():
    handle('help')
    results = output.getvalue()
    assert 'Add or update a user to the database' in results

def test_adduser():
    handle(['', 'adduser', 'cdent', 'crunk'])
    assert os.path.exists(os.path.join('store','users','cdent'))

