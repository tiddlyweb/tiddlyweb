"""
Test posting a wiki to a bag.
"""


import httplib2
import simplejson

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.user import User
from tiddlyweb.util import sha

from fixtures import muchdata, reset_textstore, _teststore, initialize_app

from base64 import b64encode
authorization = b64encode(u'cd\u2714nt:cowpig'.encode('utf-8'))

def setup_module(module):
    initialize_app()
    reset_textstore()
    module.store = _teststore()
    user = User(u'cd\u2714nt')
    user.set_password('cowpig')
    module.store.put(user)
    muchdata(module.store)

def test_get_sorted_tiddlers():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers.json?sort=title',
            method='GET')
    etag = response['etag']
    assert response['status'] == '200'
    tiddlers = simplejson.loads(content)
    assert tiddlers[0]['title'] == 'tiddler0'
    assert tiddlers[0]['uri'] == 'http://our_test_domain:8001/bags/bag0/tiddlers/tiddler0'

    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers.json?sort=title',
            method='GET')
    etag2 = response['etag']
    assert etag == etag2

    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers.json?sort=title',
            method='GET',
            headers={'if-none-match': etag})
    assert response['status'] == '304'

    # confirm head
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers.json?sort=title',
            method='HEAD',
            headers={'if-none-match': etag})
    assert response['status'] == '304'

    # confirm head
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers.json?sort=title',
            method='HEAD')
    assert response['status'] == '200'
    assert content == ''

def test_get_tiddlers_with_unicode_user():
    """
    Cover a bug in sendtiddlers related to unicode users.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers.json?sort=title',
            method='GET',
            headers={'Content-Type': 'text/plain',
                'Authorization': 'Basic %s' % authorization})
    assert response['status'] == '200'


def test_get_selected_sorted_limited_tiddlers():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers.json?select=title:!tiddler1;select=title:!tiddler0;sort=title;limit=1',
            method='GET')
    assert response['status'] == '200'
    tiddlers = simplejson.loads(content)
    assert len(tiddlers) == 1
    assert tiddlers[0]['title'] == 'tiddler2'

def test_not_post_to_bag_tiddlers():
    content = "HI EVERYBODY!"
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/wikibag/tiddlers',
            method='POST', headers={'Content-Type': 'text/x-tiddlywiki'}, body=content)

    assert response['status'] == '405'

