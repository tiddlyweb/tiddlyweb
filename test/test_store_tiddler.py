"""
Exploratory testing for storing tiddlers.

Prequisites:

    * We know which bag this tiddler belongs to.
    * We've already established authorization to write.

"""

import os
import sys
sys.path.append('.')

from tiddlyweb.store import Store
from fixtures import bagone

expected_stored_filename = 'store/bags/bagone/tiddlers/TiddlerOne'
expected_stored_content = """some
stuff
that
"""

def setup_module(module):
    """
    Need to clean up the store here.
    """
    #os.unlink(expected_stored_filename)
    #os.rmdir

def test_simple_save():
    """
    Non-working api investigation code.

    Make the assertion messages better!
    """

    store = Store('text')
    store.save(bag=bagone, tiddlers=[bagone.list_tiddlers()[0]])

    assert os.path.exists(expected_stored_filename), 'path is created'

    f = file(expected_stored_filename)
    content = f.read()

    assert content == expected_stored_content, 'stored content is as expected'

