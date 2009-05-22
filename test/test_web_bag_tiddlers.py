"""
Test posting a wiki to a bag.
"""

import sys
sys.path.append('.')

from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2
import simplejson

from tiddlyweb.model.bag import Bag

from fixtures import muchdata, reset_textstore, _teststore

def setup_module(module):
    from tiddlyweb.web import serve
    # we have to have a function that returns the callable,
    # Selector just _is_ the callable
    def app_fn():
        return serve.load_app()
    #wsgi_intercept.debuglevel = 1
    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('our_test_domain', 8001, app_fn)

    reset_textstore()
    module.store = _teststore()
    muchdata(module.store)

def test_get_sorted_tiddlers():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers.json?sort=title',
            method='GET')
    assert response['status'] == '200'
    tiddlers = simplejson.loads(content)
    assert tiddlers[0]['title'] == 'tiddler0'

def test_post_wiki_to_bag():
    bag = Bag('wikibag')
    store.put(bag)

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers.wiki',
            method='GET')

    assert response['status'] == '200'

    response, content = http.request('http://our_test_domain:8001/bags/wikibag/tiddlers',
            method='POST', headers={'Content-Type': 'text/x-tiddlywiki'}, body=content)

    assert response['status'] == '204'
    assert response['location'] == 'http://our_test_domain:8001/bags/wikibag/tiddlers'

def test_post_not_wiki_to_bag():
    content = "HI EVERYBODY!"
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/wikibag/tiddlers',
            method='POST', headers={'Content-Type': 'text/x-tiddlywiki'}, body=content)

    assert response['status'] == '400'

def test_post_not_wiki__type_to_bag():
    content = "HI EVERYBODY!"
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/wikibag/tiddlers',
            method='POST', headers={'Content-Type': 'text/plain'}, body=content)

    assert response['status'] == '415'
