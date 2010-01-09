"""
Test handling of loading external stuff in twanager.
"""

from tiddlyweb.manage import _external_load
from tiddlyweb.config import config as global_config

config = {
        'monkey': 'bar',
        }

def test_load_file():
    args = _external_load(['twanager', '--load', 'test/test_external_load.py', 'foobar'], global_config)
    assert args == ['twanager', 'foobar']
    assert global_config['monkey'] == 'bar'

def test_load_module():
    args = _external_load(['twanager', '--load', 'test.test_external_load', 'foobar'], global_config)
    assert args == ['twanager', 'foobar']
    assert global_config['monkey'] == 'bar'
