
import httplib2
import random
import string

from .fixtures import reset_textstore, initialize_app, _teststore

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler


RELEVANT_HEADERS = [
        'cache-control',
        'etag',
        'vary',
        'last-modified']


def setup_module(module):
    initialize_app()
    reset_textstore()
    module.store = _teststore()
    http = httplib2.Http()
    module.http = http


def _random_name(length=5):
        return ''.join(random.choice(string.lowercase) for i in range(length))


def test_get_tiddler():
    bag = Bag(_random_name())
    store.put(bag)

    tiddler = Tiddler(_random_name(), bag.name)
    tiddler.text = _random_name(10)
    store.put(tiddler)

    _get_entity('http://our_test_domain:8001/bags/%s/tiddlers/%s' % (
        bag.name, tiddler.title), test_last_modified=True)


def test_get_maxage_tiddler():
    bag = Bag(_random_name())
    store.put(bag)

    tiddler = Tiddler(_random_name(), bag.name)
    tiddler.text = _random_name(10)
    tiddler.fields['_cache-max-age'] = '3600'
    store.put(tiddler)

    _get_entity('http://our_test_domain:8001/bags/%s/tiddlers/%s' % (
        bag.name, tiddler.title), test_last_modified=True)


def test_get_bag():
    bag = Bag(_random_name())
    store.put(bag)
    _get_entity('http://our_test_domain:8001/bags/%s' % bag.name)


def test_get_recipe():
    recipe = Recipe(_random_name())
    store.put(recipe)
    _get_entity('http://our_test_domain:8001/recipes/%s' % recipe.name)


def test_get_tiddlers():
    bag = Bag(_random_name())
    store.put(bag)

    for i in range(10):
        tiddler = Tiddler(_random_name(), bag.name)
        store.put(tiddler)

    _get_entity('http://our_test_domain:8001/bags/%s/tiddlers' % bag.name,
            test_last_modified=True)


def _get_entity(uri, test_last_modified=False):
    """
    Get a uri and confirm that for those relevant headers
    in a 200 response, the same things are there for a
    304 response.
    """
    response, content = http.request(uri,
        method='GET')

    assert response['status'] == '200', content
    response_200 = response
    etag = response['etag']
    if 'last-modified' in response:
        last_modified = response['last-modified']
        

    response, content = http.request(uri,
        headers={'If-None-Match': etag},
        method='GET')

    assert response['status'] == '304', content
    response_304 = response

    for header in RELEVANT_HEADERS:
        if header in response_200:
            assert header in response_304
            assert response_200[header] == response_304[header]

    if test_last_modified:
        response, content = http.request(uri,
                headers={'If-Modified-Since': last_modified},
                method='GET')
        response_lm_304 = response

        for header in RELEVANT_HEADERS:
            if header in response_200:
                assert header in response_lm_304
                assert response_200[header] == response_lm_304[header]
