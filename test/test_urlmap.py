#!/usr/bin/env python

import selector
import string
import simplejson

from http_runner import *

def fixup(pattern):
    for replaceme in ['^', '\\', '(', ')', '?', '$', '[/]+', '[/.]+', '>']:
        pattern = pattern.replace(replaceme, '')
    pattern = pattern.replace('P<', '$')
    pattern = pattern.replace('.$format', '')
    return pattern


def filled_pattern(pattern):
    template = string.Template(pattern)
    info = {
            'recipe_name': 'recipeurlmap1',
            'tiddler_name': 'tiddlerurlmap1',
            'bag_name': 'bagurlmap1',
            'revision': '1',
            'challenger': 'cookie_form',
            }
    return template.substitute(**info)


def data_from_pattern(pattern):
    data = {}
    if '$recipe_name' in pattern:
        if '$tiddler_name' in pattern:
            data['text'] = 'oh hai'
        else:
            data['recipe'] = [
                    ['bagurlmap1', ''],
                    ]
    if '$bag_name' in pattern:
        if '$tiddler_name' in pattern:
            data['text'] = 'oh hai'
        else:
            data['description'] = "hey buddy"
    return simplejson.dumps(data)


def figure_tests(app):
    tests = []
    for pattern, methods in app.mappings:
        pattern = fixup(pattern.pattern)
        for method_type in methods:
            test = {}
            test['method'] = method_type
            test['name'] = '%s:%s' % (method_type, pattern)
            test['desc'] = test['name']
            test['url'] = filled_pattern(pattern)
            if 'challenge' in test['url']:
                continue
            if 'revisions' in test['url']:
                continue
            if 'search' in test['url']:
                test['url'] = test['url'] + '?q=hai'
                test['expected'] = ['tiddlerurlmap1']
            if method_type == 'GET':
                test['status'] = '200'
                test['request_headers'] = {
                        'accept': 'application/json',
                        }
                if 'recipe_name' in pattern and 'tiddler_name' in pattern:
                    test['expected'] = ['oh hai']
                elif 'tiddlers' in pattern and 'tiddler_name' not in pattern:
                    test['expected'] = ['tiddlerurlmap1']
            elif method_type == 'DELETE':
                test['status'] = '204'
                if 'recipe_name' in pattern and 'tiddler_name' in pattern:
                    continue
            elif method_type == 'PUT':
                test['status'] = '204'
                test['data'] = data_from_pattern(pattern)
                test['request_headers'] = {
                        'content-type': 'application/json',
                        }
            else:
                continue
            tests.append(test)
    def test_sorter(test):
        method = test['method']
        if method == 'DELETE':
            key = test['method'] + 'x' * len(test['name'])
        else:
            key = test['method'] + 'x' * (70 - len(test['name']))
        return key
    return sorted(tests, key=test_sorter, reverse=True)


def setup_module(module):
    tests = do_run()
    http_test(tests, 'http://our_test_domain:8001')
    # the below is for testing tiddlynode
    #http_test(tests, 'http://127.0.0.1:8000')


def do_run():
    app = selector.Selector(mapfile='tiddlyweb/urls.map')
    return figure_tests(app)


if __name__ == '__main__':
    do_run()

