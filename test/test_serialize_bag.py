
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

expected_sort_string = """tiddlers/TiddlerThree
tiddlers/TiddlerTwo
tiddlers/TiddlerOne"""

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

def test_serialized_sort():

    serializer = Serializer(bagfour, 'text', sortkey=lambda x: x.content)
    string = serializer.to_string()

    assert string == expected_sort_string, \
            'serialized bag looks like we expect. should be %s, got %s' \
            % (expected_string, string)

    assert '%s' % serializer == expected_sort_string, \
            'serializer goes to string as expected_sort_string'

