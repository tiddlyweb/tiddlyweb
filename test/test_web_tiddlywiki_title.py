
import sys
import os
sys.path.append('.')

from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2

from tiddlyweb.model.tiddler import Tiddler

from fixtures import muchdata, reset_textstore, teststore

def setup_module(module):
    from tiddlyweb.web import serve
    # we have to have a function that returns the callable,
    # Selector just _is_ the callable
    def app_fn():
        return serve.load_app()
    #wsgi_intercept.debuglevel = 1
    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('our_test_domain', 8001, app_fn)

    module.store = teststore()
    reset_textstore()
    muchdata(module.store)

def test_get_wiki():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers.wiki',
            method='GET')

    assert response['status'] == '200'
    assert response['content-type'] == 'text/html; charset=UTF-8'
    assert '\n<title>\nTiddlyWeb Loading\n</title>\n' in content
    assert 'i am tiddler 8' in content

def test_get_wiki_with_title():
    tiddler = Tiddler('SiteTitle')
    tiddler.bag = 'bag1'
    tiddler.text = 'Wow //cow// moo'

    store.put(tiddler)

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers.wiki',
            method='GET')

    assert response['status'] == '200'
    assert '\n<title>\nWow cow moo\n</title>\n' in content
    assert 'Wow //cow// moo' in content

    tiddler = Tiddler('SiteSubtitle')
    tiddler.bag = 'bag1'
    tiddler.text = 'MooCow'
    store.put(tiddler)

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers.wiki',
            method='GET')

    assert response['status'] == '200'
    assert '<title>\nWow cow moo - MooCow\n</title>' in content
    assert 'MooCow' in content

    tiddler = Tiddler('SiteTitle')
    tiddler.bag = 'bag1'
    store.delete(tiddler)

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers.wiki',
            method='GET')

    assert response['status'] == '200'
    assert '<title>\nMooCow\n</title>' in content
    assert 'MooCow' in content
