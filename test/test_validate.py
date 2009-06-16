
import sys
sys.path.insert(0, '.')

import py.test

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.web.validator import validate_bag, validate_tiddler, InvalidTiddlerError
import tiddlyweb.web.validator

def check_for_text(tiddler, environ):
    if 'foobar' not in tiddler.text:
        raise InvalidTiddlerError('missing "foobar" in tiddler.text')

def modify_text(tiddler, environ):
    tiddler.text = tiddler.text.replace('foobar', 'FOOBAR')

tiddlyweb.web.validator.TIDDLER_VALIDATORS = [
        check_for_text,
        modify_text,
        ]

def setup_module(module):
    pass

def test_validate_tiddler():
    tiddler = Tiddler('foobar', 'barney')
    tiddler.text = 'I am a dinosaur'
    tiddler.tags = ['tag1', 'tag2']

    py.test.raises(InvalidTiddlerError, 'validate_tiddler(tiddler)')

    tiddler.text = 'I am a dinosaur who likes to foobar'

    validate_tiddler(tiddler)

    assert 'FOOBAR' in tiddler.text

def test_validate_bag_desc():
    bag = Bag('barney')
    bag.desc = '<script>alert("foo");</script>'

    validate_bag(bag)

    assert bag.desc == '&lt;script&gt;alert("foo");&lt;/script&gt;'

