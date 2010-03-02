#!/usr/bin/python

"""
This is a CGI script that can be used for running
TiddlyWeb under a web server, instead of using the
sever that is built in.

Put the cgi somewhere your web server can run cgis. You
can rename it if you like. Make sure the file is executable.

If you are using the text store (you probably are) follow
the instructions in COOKBOOK to make a text store directory
structure somewhere. The directory hierarchy must be writable 
by the web server. In tiddlywebconfig.py you need to set server_store
and store_root to point to that directory:

    'server_store': ['text', {'store_root': '/some/path/to/store'}],
        'server_prefix': '/~cdent/tw/index.cgi',
        'server_host': {
            'scheme': 'http',
            'host': 'burningchrome.com',
            'port': '80'},

You need to choose a location where your tiddlywebconfig.py will
live. This is also where you should put any plugins you are using
and where tiddlyweb.log will be written. You may need to create
tiddlyweb.log yourself, and set its permissions so the server can
write to it.

Whatever location you choose for your tiddlywebconfig.py set to
tiddlywebconfig_dir to that directory, in the script below.

You will need to set server_prefix and server_host in the
tiddlywebconfig.py in the location that you choose.

        'server_prefix': '/~cdent/tw/index.cgi',
        'server_host': {
            'scheme': 'http',
            'host': 'burningchrome.com',
            'port': '80'},

It is a good idea for your store directory and tiddlywebconfig_dir
to be different places.

You may need to change the PYTHON_EGG_CACHE setting.

See http://tiddlyweb.peemore.com for general documentation and
http://bengillies.net/.a/#%5B%5BRunning%20on%20TiddlyWeb%2C%20Part%20One%5D%5D
for an installation tutorial, specifically for people who
do not have root access on their server.
"""

import os
import sys

tiddlywebconfig_dir = '/home/cdent/hot_html/tw'

os.environ['PYTHON_EGG_CACHE'] = '/tmp'
os.chdir(tiddlywebconfig_dir)
sys.path.insert(0, tiddlywebconfig_dir)

from wsgiref.handlers import BaseCGIHandler
from tiddlyweb.web import serve

def start():
    app = serve.load_app(app_prefix='')
    if not 'PATH_INFO' in os.environ:
        os.environ['PATH_INFO'] = '/'
    BaseCGIHandler(sys.stdin, sys.stdout, sys.stderr, os.environ).run(app)

if __name__ == '__main__':
    start()
