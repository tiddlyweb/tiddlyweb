"""
Test handling of loading external stuff in twanager.
"""

from tiddlyweb.manage import handle
from tiddlyweb.config import config as global_config


config = {
        'monkey': 'bar',
        }


def test_load_file():
    handle(['twanager', '--load', 'test/test_external_load.py', 'info'])
    assert global_config['monkey'] == 'bar'


def test_load_module():
    handle(['twanager', '--load', 'test.test_external_load', 'info'])
    assert global_config['monkey'] == 'bar'
