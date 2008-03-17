
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

expected_html_string = """<ul>
<li><a href="tiddlers/TiddlerThree">TiddlerThree</a></li>
<li><a href="tiddlers/TiddlerTwo">TiddlerTwo</a></li>
<li><a href="tiddlers/TiddlerOne">TiddlerOne</a></li>
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

def test_serialized_sort():

    serializer.object = bagfour
    serializer.sortkey = lambda x: x.content
    string = serializer.to_string()

    assert string == expected_sort_string, \
            'serialized bag looks like we expect. should be %s, got %s' \
            % (expected_string, string)

    assert '%s' % serializer == expected_sort_string, \
            'serializer goes to string as expected_sort_string'

def test_generated_html():
    html_serializer = Serializer('html')
    html_serializer.object = bagfour
    html_serializer.sortkey = lambda x: x.content
    string = html_serializer.to_string()

    assert string == expected_html_string, \
            'serialized bag looks like we expect. should be %s, got %s' \
            % (expected_html_string, string)

    assert '%s' % html_serializer == expected_html_string, \
            'serializer goes to string as expected_string, got %s' % html_serializer
