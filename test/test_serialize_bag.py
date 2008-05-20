
"""
Test turning a bag into other forms.
"""

import sys
sys.path.append('.')

import simplejson

from tiddlyweb.serializer import Serializer
from tiddlyweb.bag import Bag

from fixtures import bagfour

expected_string = """TiddlerOne
TiddlerTwo
TiddlerThree"""

expected_revbag_string = """TiddlerOne:None
TiddlerTwo:None
TiddlerThree:None"""

expected_html_string = """<ul>
<li><a href="/bags/bagfour/tiddlers/TiddlerOne">TiddlerOne</a></li>
<li><a href="/bags/bagfour/tiddlers/TiddlerTwo">TiddlerTwo</a></li>
<li><a href="/bags/bagfour/tiddlers/TiddlerThree">TiddlerThree</a></li>
</ul>"""

expected_html_revbag_string = """<ul>
<li><a href="/bags/bagfour/tiddlers/TiddlerOne/revisions/None">TiddlerOne:None</a></li>
<li><a href="/bags/bagfour/tiddlers/TiddlerTwo/revisions/None">TiddlerTwo:None</a></li>
<li><a href="/bags/bagfour/tiddlers/TiddlerThree/revisions/None">TiddlerThree:None</a></li>
</ul>"""

def setup_module(module):
    module.serializer = Serializer('text')

def test_generated_string():
    serializer.object = bagfour
    string = serializer.to_string()

    assert string == expected_string
    assert '%s' % serializer == expected_string

def test_generated_string_with_revbag():
    serializer.object = bagfour
    bagfour.revbag = True
    string = serializer.to_string()

    assert string == expected_revbag_string
    assert '%s' % serializer == expected_revbag_string
    bagfour.revbag = False

def test_generated_html():
    html_serializer = Serializer('html')
    html_serializer.object = bagfour
    string = html_serializer.to_string()

    assert string == expected_html_string
    assert '%s' % html_serializer == expected_html_string

def test_generated_wiki():
    wiki_serializer = Serializer('wiki')
    wiki_serializer.object = bagfour
    string = wiki_serializer.to_string()

    assert '<div title="TiddlerOne' in string
    assert '<div title="TiddlerTwo' in string
    assert '<div title="TiddlerThree' in string

def test_generated_html_with_revbag():
    html_serializer = Serializer('html')
    bagfour.revbag = True
    html_serializer.object = bagfour
    string = html_serializer.to_string()

    assert string == expected_html_revbag_string
    assert '%s' % html_serializer == expected_html_revbag_string
    bagfour.revbag = False

def test_json_to_bag():
    serializer = Serializer('json')

    json_string = simplejson.dumps(dict(policy='i wish i was'))
    newbag = Bag('bagho')
    serializer.object = newbag
    serializer.from_string(json_string)

    assert newbag.name == 'bagho'
    assert newbag.policy == 'i wish i was'

