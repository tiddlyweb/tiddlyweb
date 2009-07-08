"""
Test extended fields on tiddlers via the HTTP API.
"""


from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2
import simplejson
import simplejson

from tiddlyweb.serializer import Serializer

from fixtures import reset_textstore, _teststore, muchdata

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

def test_put_tiddler_with_fields():
    tiddler_dict = {
            'tags': ['one','two','three'],
            'text': 'hello',
            'fields': {
                'server.first': 'base',
                'field1': 'value1',
                'field2': 'value2',
                },
            }
    tiddler_json = simplejson.dumps(tiddler_dict)

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/feebles',
            method='PUT', headers={'Content-Type': 'application/json'}, body=tiddler_json)

    assert response['status'] == '204'

def test_get_tiddler_with_fields():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/feebles.json',
            method='GET')

    assert response['status'] == '200'
    tiddler_dict = simplejson.loads(content)
    assert tiddler_dict['text'] == 'hello'
    assert tiddler_dict['fields']['field1'] == 'value1'
    assert tiddler_dict['fields']['field2'] == 'value2'
    assert not tiddler_dict['fields'].has_key('server.first')
