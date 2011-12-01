"""
Test turning a tiddler into other forms.
"""

import simplejson
import py.test

from base64 import b64encode

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.serializer import Serializer, TiddlerFormatError
from tiddlyweb.config import config

expected_string = """modifier: test@example.com
created: 
modified: 200803030303
type: None
tags: foobar [[foo bar]]

Hello, I'm the content.
"""

# cosmic rays have injected noise into this tiddler string
bad_string = """modifiXr: test@example.com
created: 
modiFied: 200803030303
type: None
tags:foobar [[foo bar]]

Hello, I'm the content.
"""

expected_json_string = '{"created": "", "text": "Hello, I\'m the content.", "modifier": "test@example.com", "modified": "200803030303", "tags": ["foobar", "foo bar"]}'

tiddler = Tiddler('test tiddler')
tiddler.bag = 'snoop'
tiddler.modifier = 'test@example.com'
tiddler.tags = ['foobar', 'foo bar']
tiddler.text = "Hello, I'm the content."
tiddler.modified = '200803030303'

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
    serializer = Serializer('json', environ={'tiddlyweb.config': config})
    serializer.object = tiddler
    string = serializer.to_string()

    info = simplejson.loads(string)

    assert info['title'] == 'test tiddler'
    assert info['text'] == "Hello, I'm the content."
    assert info['uri'] == '%s://%s:%s/bags/snoop/tiddlers/test%%20tiddler' % (
            config['server_host']['scheme'],
            config['server_host']['host'],
            config['server_host']['port'])

def test_tiddler_from_json():
    serializer = Serializer('json')
    tiddler = Tiddler('test tiddler')
    serializer.object = tiddler
    serializer.from_string(expected_json_string)

    assert tiddler.title == 'test tiddler'
    assert tiddler.text == "Hello, I'm the content."

def test_tiddler_html_encode():
    serializer = Serializer('html')
    tiddler = Tiddler('jeremy found a bug')
    tiddler.bag = u'foo'
    tiddler.text = u'"Hello." I\'m > than 5 & < you.'
    serializer.object = tiddler
    string = serializer.to_string()

    assert '"Hello." I\'m &gt; than 5 &amp; &lt; you.' in string

def test_html_attribute_escape():
    tiddler = Tiddler('escape "double" quotes & &amp; in <tiddler> field values')
    tiddler.bag = u'foo "bar" baz'
    tiddler.modifier = 'Chris "sensei" Dent'
    tiddler.tags = ["foo", 'xxx "yyy" zzz']
    tiddler.fields["custom"] = u"""lorem 'ipsum' dolor "sit" amet"""
    tiddler.text = ''
    serializer = Serializer('html')
    serializer.object = tiddler
    string = serializer.to_string()

    assert r'''title="escape &quot;double&quot; quotes &amp; &amp;amp; in &lt;tiddler&gt; field values"''' in string
    assert r'''modifier="Chris &quot;sensei&quot; Dent"''' in string
    assert r'''tags="foo [[xxx &quot;yyy&quot; zzz]]"''' in string
    assert r'''custom="lorem 'ipsum' dolor &quot;sit&quot; amet"''' in string

def test_tiddler_json_base64():
    serializer = Serializer('json', environ={'tiddlyweb.config': config})
    tiddler = Tiddler('binarytiddler')
    tiddler.bag = u'foo'
    tiddler.text = file('test/peermore.png', 'rb').read()
    bininfo = tiddler.text
    b64expected = b64encode(tiddler.text)
    tiddler.type = 'image/png'
    serializer.object = tiddler
    string = serializer.to_string()
    info = simplejson.loads(string)
    assert info['text'] == b64expected

    tiddler = serializer.from_string(string)
    assert tiddler.text == bininfo

    info['text'] = '..badbinary..'
    string = simplejson.dumps(info)
    py.test.raises(TiddlerFormatError, 'serializer.from_string(string)')

def test_tiddler_json_render():
    serializer = Serializer('json', environ={'tiddlyweb.query': {
        'render': [1]}, 'tiddlyweb.config': config})
    tiddler = Tiddler('htmltest')
    tiddler.text = '!Hi\n//you//'
    tiddler.bag = 'snoop'

    serializer.object = tiddler

    output = serializer.to_string()
    info = simplejson.loads(output)
    assert info['render'] == '<pre>\n!Hi\n//you//</pre>\n'

def test_tiddler_no_text():
    serializer = Serializer('text')
    tiddler = Tiddler('hello')
    serializer.object = tiddler
    header, body = serializer.to_string().split('\n\n')
    assert 'None' not in body
