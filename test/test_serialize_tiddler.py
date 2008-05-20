
"""
Test turning a tiddler into other forms.

Currently this test and the code in general does not
pay attention to modified and created fields in the
tiddler. This will be added later. For now it is
just in the way.
"""

import sys
sys.path.append('.')

import simplejson
import py.test

from tiddlyweb.tiddler import Tiddler
from tiddlyweb.serializer import Serializer, TiddlerFormatError

expected_string = """modifier: test@example.com
created: 
modified: 200803030303
tags: foobar [[foo bar]]

Hello, I'm the content.
"""

# cosmic rays have injected noise into this tiddler string
bad_string = """modifiXr: test@example.com
created: 
modiFied: 200803030303
tgs: foobar [[foo bar]]

Hello, I'm the content.
"""

expected_json_string = '{"created": "", "text": "Hello, I\'m the content.", "modifier": "test@example.com", "modified": "200803030303", "tags": ["foobar", "foo bar"]}'

tiddler = Tiddler(
        title = 'test tiddler',
        modifier = 'test@example.com',
        tags = ['foobar', 'foo bar'],
        text = "Hello, I'm the content.",
        modified = '200803030303'
        )

def setup_module(module):
    pass

def test_generated_txt_string():
    serializer = Serializer('text')
    serializer.object = tiddler
    string = serializer.to_string()

    assert string == expected_string, \
            'serialized recipe looks like we expect. should be %s, got %s' \
            % (expected_string, string)

    assert '%s' % serializer == expected_string, \
            'serializer goes to string as expected_string'

def test_bad_string_raises():
    serializer = Serializer('text')
    foobar = Tiddler('foobar')
    serializer.object = foobar

    py.test.raises(TiddlerFormatError, 'serializer.from_string(bad_string)')

def test_generated_json_string():
    serializer = Serializer('json')
    serializer.object = tiddler
    string = serializer.to_string()

    info = simplejson.loads(string)

    assert info['title'] == 'test tiddler'
    assert info['text'] == "Hello, I'm the content."

def test_tiddler_from_json():
    serializer = Serializer('json')
    tiddler = Tiddler('test tiddler')
    serializer.object = tiddler
    serializer.from_string(expected_json_string)

    assert tiddler.title == 'test tiddler'
    assert tiddler.text == "Hello, I'm the content."



