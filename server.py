
import os
from tiddlyweb.web import serve
from tiddlyweb.store import Store
from test import fixtures

def start():
    if not os.path.exists(fixtures.textstore.store_dirname):
        fixtures.reset_textstore()
        stores = Store('text')
        fixtures.muchdata(stores)
    serve.start_simple('./urls.map', 8080)

if __name__ == '__main__':
    start()
