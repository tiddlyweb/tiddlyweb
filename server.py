
import os
from tiddlyweb.web import serve
from test import fixtures

def start():
    if not os.path.exists(fixtures.textstore.store_dirname):
        fixtures.reset_textstore()
    serve.start_simple('./urls.map', 8080)

if __name__ == '__main__':
    start()
