"""
Make sure that tiddler fields which are not strings
are stringified, otherwise, the text serialization will 
assplode.
"""

from tiddlyweb.serializer import Serializer
from tiddlyweb.model.tiddler import Tiddler


def setup_module(module):
    pass


def test_float_field():
    tiddler = Tiddler('foo', 'bar')
    tiddler.fields['float'] = 100.5

    serializer = Serializer('text')
    serializer.object = tiddler
    assert '100.5' in '%s' % serializer
