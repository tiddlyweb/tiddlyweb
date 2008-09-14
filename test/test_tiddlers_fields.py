"""
Test extended fields on tiddlers.
Some tiddlers have additional fields what we don't
know about ahead of time, but we'd like to handle.
Most straightforward things to do here seems to be
to do what TiddlyWiki does: have a fields field.
"""

import sys
sys.path.append('.')

from tiddlyweb.serializer import Serializer
from tiddlyweb.tiddler import Tiddler
from tiddlyweb.bag import Bag

from fixtures import reset_textstore, teststore

def setup_module(module):
    reset_textstore()
    module.store = teststore()

def test_tiddler_has_fields():
    tiddler = Tiddler('feebles')
    assert hasattr(tiddler, 'fields')

def test_tiddler_fields_dict():
    tiddler = Tiddler('feebles')
    assert type(tiddler.fields) == dict

def test_tiddler_fields_contains_stuff():
    tiddler = Tiddler('feebles')
    tiddler.fields = {'this':'is cool', 'so':'is that'}
    assert tiddler.fields['this'] == 'is cool'
    assert tiddler.fields['so'] == 'is that'

def test_tiddler_fields_are_stored():
    bag = Bag('bag0')
    store.put(bag)
    tiddler = Tiddler('feebles', bag='bag0')
    tiddler.fields = {'field1': 'value1', 'field2': 'value2'}
    store.put(tiddler)

    tiddler_second = Tiddler('feebles', bag='bag0')
    store.get(tiddler_second)
    assert tiddler_second.fields['field1'] == 'value1'
    assert tiddler_second.fields['field2'] == 'value2'

def test_tiddler_fields_ignore_server():
    bag = Bag('bag0')
    store.put(bag)
    tiddler = Tiddler('serverimpostor', bag='bag0')
    tiddler.fields = {'field1': 'value1', 'server.host': 'value1', 'server.type': 'value2'}
    store.put(tiddler)

    tiddler_second = Tiddler('serverimpostor', bag='bag0')
    store.get(tiddler_second)
    assert tiddler_second.fields['field1'] == 'value1'
    assert 'server.host' not in tiddler_second.fields.keys()
    assert 'server.type' not in tiddler_second.fields.keys()

# these following rely on the previous
def test_tiddler_fields_as_text():
    tiddler = Tiddler('feebles', bag='bag0')
    store.get(tiddler)
    serializer = Serializer('text')
    serializer.object = tiddler
    text_of_tiddler = serializer.to_string()
    assert 'field1: value1\n' in text_of_tiddler
    assert 'field2: value2\n' in text_of_tiddler

#def test_tiddler_fields_as_json():
#def test_fields_in_tiddler_put():
#def test_fields_in_tiddler_get():
