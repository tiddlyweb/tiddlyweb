
"""
Test turning a recipe into other forms.
"""

import sys
sys.path.append('.')
from tiddlyweb.tiddler import Tiddler
from tiddlyweb.serializer import Serializer

expected_string = """name: test tiddler
author: test@example.com
tags: [[foo bar]] foobar

Hello, I'm the content.
"""

def setup_module(module):
    pass

def test_generated_string():

    tiddler = Tiddler(
            name = 'test tiddler',
            author = 'test@example.com',
            tags = ['foobar', 'foo bar'],
            content = "Hello, I'm the content."
            )

    serializer = Serializer(tiddler, 'text')
    string = serializer.to_string()

    assert string == expected_string, \
            'serialized recipe looks like we expect. should be %s, got %s' \
            % (expected_string, string)

    assert '%s' % serializer == expected_string, \
            'serializer goes to string as expected_string'
