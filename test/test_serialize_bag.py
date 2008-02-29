
"""
Test turning a bag into other forms.
"""

import sys
sys.path.append('.')
from tiddlyweb.serializer import Serializer

from fixtures import bagfour

expected_string = """tiddlers/TiddlerOne
tiddlers/TiddlerThree
tiddlers/TiddlerTwo"""

def setup_module(module):
    pass

def test_generated_string():

    serializer = Serializer(bagfour, 'text')
    string = serializer.to_string()

    assert string == expected_string, \
            'serialized bag looks like we expect. should be %s, got %s' \
            % (expected_string, string)

    assert '%s' % serializer == expected_string, \
            'serializer goes to string as expected_string'
