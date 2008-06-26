
import os
import sys
from tiddlyweb.web import serve
from tiddlyweb.config import config
from tiddlyweb.store import Store
from test import fixtures

config['extension_types']['atom'] = 'application/atom+xml'
config['serializers']['application/atom+xml'] = ['atom.atom', 'application/atom+xml; charset=UTF-8']
config['serializers']['text/html'] = ['atom.htmlatom', 'text/html; charset=UTF-8']

def start(hostname, port):
    if not os.path.exists(fixtures.textstore.store_dirname):
        fixtures.reset_textstore()
        stores = Store('text')
        fixtures.muchdata(stores)
    print '%s' % config
    serve.start_cherrypy('./urls.map', hostname, int(port))

if __name__ == '__main__':
    start(sys.argv[1], sys.argv[2])
