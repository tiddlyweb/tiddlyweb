
"""
Test turning a bag into other forms.
"""

import sys
sys.path.append('.')
from tiddlyweb.serializer import Serializer

from fixtures import bagfour

expected_string = """tiddlers/TiddlerOne
tiddlers/TiddlerTwo
tiddlers/TiddlerThree"""

expected_html_string = """<ul>
<li><a href="/bags/bagfour/tiddlers/TiddlerOne">TiddlerOne</a></li>
<li><a href="/bags/bagfour/tiddlers/TiddlerTwo">TiddlerTwo</a></li>
<li><a href="/bags/bagfour/tiddlers/TiddlerThree">TiddlerThree</a></li>
</ul>"""

def setup_module(module):
    module.serializer = Serializer('text')

def test_generated_string():

    serializer.object = bagfour
    string = serializer.to_string()

    assert string == expected_string, \
            'serialized bag looks like we expect. should be %s, got %s' \
            % (expected_string, string)

    assert '%s' % serializer == expected_string, \
            'serializer goes to string as expected_string'

def test_generated_html():
    html_serializer = Serializer('html')
    html_serializer.object = bagfour
    string = html_serializer.to_string()

    print bagfour

    assert string == expected_html_string, \
            'serialized bag looks like we expect. should be %s, got %s' \
            % (expected_html_string, string)

    assert '%s' % html_serializer == expected_html_string, \
            'serializer goes to string as expected_string, got %s' % html_serializer
