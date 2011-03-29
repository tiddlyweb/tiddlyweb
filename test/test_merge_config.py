"""
Test that merging config results in what's
expected when updating dicts. There had been some
problems in this area, so here we try to lay down
a bit of reality.
"""
from copy import deepcopy

from tiddlyweb.config import config as global_config
from tiddlyweb.util import merge_config

def setup_module(module):
    """
    Protect against py.test's new collection mechanism
    which carries about globals during the test collection phase.
    """
    if 'selector' in global_config:
        del global_config['selector']


def test_merge_sub_addition():
    config = deepcopy(global_config)
    new_config = {
            'serializers': {
                'text/bar': ['bar', 'type'],
                }
            }
    merge_config(config, new_config, reconfig=False)
    assert 'text/bar' in config['serializers']
    assert config['serializers']['text/bar'] == ['bar', 'type']
    assert 'text/html' in config['serializers']
    assert 'html' in config['serializers']['text/html']
    assert 'default_serializer' in config
    assert config['default_serializer'] == 'text/html'


def test_merge_sub_replace():
    config = deepcopy(global_config)
    new_config = {
            'serializers': {
                'text/html': ['bar', 'type'],
                }
            }
    merge_config(config, new_config, reconfig=False)
    assert 'text/html' in config['serializers']
    assert config['serializers']['text/html'] == ['bar', 'type']
    assert 'application/json' in config['serializers']
    assert 'json' in config['serializers']['application/json']
    assert 'default_serializer' in config
    assert config['default_serializer'] == 'text/html'


def test_merge_addition():
    config = deepcopy(global_config)
    new_config = {
            'extra': {
                'stuff': ['one', 'two'],
                }
            }
    merge_config(config, new_config, reconfig=False)
    assert 'extra' in config
    assert 'stuff' in config['extra']
    assert 'one' in config['extra']['stuff']


def test_merge_addition_double_over_no_twc():
    config = deepcopy(global_config)
    custom_config = {
            'nextra': {
                'show': ['three', 'four'],
                'stuff': ['five', 'six'],
                }
            }
    plugin_config = {
            'nextra': {
                'show': ['seven', 'eight']
                }
            }
    merge_config(config, custom_config, reconfig=False)
    assert 'nextra' in config
    assert 'stuff' in config['nextra']
    assert 'five' in config['nextra']['stuff']
    assert 'show' in config['nextra']
    assert 'three' in config['nextra']['show']
    merge_config(config, plugin_config, reconfig=False)
    assert 'nextra' in config
    assert 'stuff' in config['nextra']
    assert 'five' in config['nextra']['stuff']
    assert 'show' in config['nextra']
    assert 'seven' in config['nextra']['show']
    merge_config(config, custom_config, reconfig=False)
    assert 'show' in config['nextra']
    assert 'seven' not in config['nextra']['show']


def test_merge_addition_double_over_twc():
    new_config = {
            'extra': {
                'show': ['three', 'four'],
                'stuff': ['five', 'six'],
                }
            }
    merge_config(global_config, new_config)
    assert 'extra' in global_config
    assert 'stuff' in global_config['extra']
    assert 'one' in global_config['extra']['stuff']
    assert 'show' in global_config['extra']
    assert 'three' in global_config['extra']['show']
