
import urllib
import httplib2
import simplejson

from fixtures import reset_textstore, _teststore, initialize_app
from tiddlyweb.model.bag import Bag

def setup_module(module):
    initialize_app()
    reset_textstore()
    module.store = _teststore()

    for i in xrange(5):
        bag = Bag('bag%s' % i)
        module.store.put(bag)

def test_get_bags_txt():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags',
            headers={'Accept': 'text/plain'},
            method='GET')

    assert response['status'] == '200'
    for i in xrange(5):
        assert 'bag%s\n' % i in content
    assert 'etag' in response
    etag = response['etag']

    response, content = http.request('http://our_test_domain:8001/bags',
            headers={'Accept': 'text/plain', 'if-none-match': etag},
            method='GET')
    assert response['status'] == '304', content

    response, content = http.request('http://our_test_domain:8001/bags',
            headers={'Accept': 'text/plain', 'if-none-match': etag + 'foo'},
            method='GET')
    assert response['status'] == '200', content


def test_get_bags_filters():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags?select=name:bag1',
            headers={'Accept': 'text/plain'},
            method='GET')

    assert response['status'] == '200', content
    assert 'bag1\n' in content
    assert 'bag2\n' not in content

def test_get_bags_filters():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags?select=rbag:figgy',
            headers={'Accept': 'text/plain'},
            method='GET')

    assert response['status'] == '400', content
    assert 'malformed filter' in content

def test_get_bags_selected_sorted_filters():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags?select=name:>bag2',
            headers={'Accept': 'text/plain'},
            method='GET')

    assert response['status'] == '200', content
    assert 'bag1\n' not in content
    assert 'bag2\n' not in content
    assert 'bag3\n' in content

def test_get_bags_sorted_filters():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags?sort=-name',
            headers={'Accept': 'text/plain'},
            method='GET')

    assert response['status'] == '200', content
    assert 'bag4\nbag3\nbag2\nbag1\nbag0' in content

def test_get_bags_sorted_limitedfilters():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags?sort=-name;limit=1,1',
            headers={'Accept': 'text/plain'},
            method='GET')

    assert response['status'] == '200', content
    assert content == 'bag3\n'

def test_get_bags_bad_filter():
    http = httplib2.Http()
    response, content = http.request(
            'http://our_test_domain:8001/bags?sort=title',
            headers={'Accept': 'text/plain'},
            method='GET')

    assert response['status'] == '400', content
    assert 'malformed filter' in content
