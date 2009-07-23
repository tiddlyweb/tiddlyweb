
"""
Test turning a bag into other forms.
"""

import simplejson

from tiddlyweb.serializer import Serializer
from tiddlyweb.model.bag import Bag
from tiddlyweb.config import config

from fixtures import tiddlers as some_tiddlers


def setup_module(module):
    module.serializer = Serializer('text')

def tiddler_source():
    for tiddler in some_tiddlers:
        tiddler.bag = None
        yield tiddler
    return 

def test_generate_json():
    bagfour = Bag('four')
    serializer = Serializer('json')
    bagfour.desc = 'a tasty little bag'
    bagfour.policy.manage = ['NONE']
    serializer.object = bagfour
    string = serializer.to_string()

    json = simplejson.loads(string)
    assert json['policy']['manage'] == ['NONE']
    assert json['desc'] == 'a tasty little bag'


def test_generated_string():
    bagfour = Bag('four', source=tiddler_source())
    string = ''.join(serializer.list_tiddlers(bagfour))

    assert 'TiddlerOne' in string
    assert 'TiddlerTwo' in string
    assert 'TiddlerThree' in string

def test_generated_string_with_revbag():
    bagfour = Bag('four', source=tiddler_source())
    bagfour.revbag = True
    string = ''.join(list(serializer.list_tiddlers(bagfour)))

    assert 'TiddlerOne:0' in string
    assert 'TiddlerTwo:0' in string
    assert 'TiddlerThree:0' in string
    bagfour.revbag = False

def test_generated_html():
    bagfour = Bag('four', source=tiddler_source())
    html_serializer = Serializer('html')
    string = ''.join(html_serializer.list_tiddlers(bagfour))
    assert '<li><a href="/bags/four/tiddlers/TiddlerOne">TiddlerOne</a></li>' in string

def test_generated_html_with_prefix():
    bagfour = Bag('four', source=tiddler_source())
    new_config = config.copy()
    new_config['server_prefix'] = '/salacious'
    environ = {'tiddlyweb.config': new_config}
    html_serializer = Serializer('html', environ)
    string = html_serializer.list_tiddlers(bagfour)

    assert '<li><a href="/salacious/bags/four/tiddlers/TiddlerOne">TiddlerOne</a></li>' in string

def test_generated_html_with_revbag():
    bagfour = Bag('four', source=tiddler_source())
    html_serializer = Serializer('html')
    bagfour.revbag = True
    string = html_serializer.list_tiddlers(bagfour)

    assert '<li><a href="/bags/four/tiddlers/TiddlerTwo/revisions/0">TiddlerTwo:0</a></li>' in string
    bagfour.revbag = False

def test_json_to_bag():
    serializer = Serializer('json')

    json_string = simplejson.dumps(dict(policy=dict(read=['user1'], manage=['NONE']), desc='simply the best'))
    newbag = Bag('bagho')
    serializer.object = newbag
    serializer.from_string(json_string)

    assert newbag.name == 'bagho'
    assert newbag.policy.read == ['user1']
    assert newbag.policy.manage == ['NONE']
    assert newbag.desc == 'simply the best'

def test_text_list():
    serializer = Serializer('text')
    bags = [Bag('bag' + str(name)) for name in xrange(2)]
    string = ''.join(list(serializer.list_bags(bags)))

    assert 'bag0' in string
    assert 'bag1' in string

def test_html_list():
    serializer = Serializer('html')
    bags = [Bag('bag' + str(name)) for name in xrange(2)]
    string = ''.join(list(serializer.list_bags(bags)))

    assert 'href="bags/bag0' in string
    assert 'href="bags/bag1' in string
