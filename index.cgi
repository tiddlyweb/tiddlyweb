#!/usr/bin/python

"""
This is a CGI script that can be used for running
TiddlyWeb under a web server, instead of using the
sever that is built in.

Put the cgi somewhere your web server can run cgis. You
can rename it if you like. Make sure the file is executable.

In the same directory as index.cgi, make a copy of or synlink
to the lib directory available in the TiddlyWeb code repo.

Place a copy of urls.map in the same directory as index.cgi
or adjust the tiddlywebconfig.py urls_map key to point to
wherever you have it.

If you are using the text store (you probably are) follow
the instructions in COOKBOOK to make a text store directory
structure somewhere. The directory hierarchy must be writable 
by the web server. Set file_store_location (below) to the
path to this directory.

Determine the URL of your CGI script. Set web_server_base
(below) to the path portion of this URL.
"""

import os
import sys

# Change this to the location of the tiddlyweb code,
# if tiddlyweb is not in sys.path
sys.path.append('/home/cdent/src/TiddlyWeb')

from wsgiref.handlers import BaseCGIHandler
from tiddlyweb.web import serve
from tiddlyweb.config import config

# where is the content stored
file_store_location = '/tmp/store'

# what's the URL to this index.cgi when access over the web
web_server_base = '/tiddlyweb/index.cgi'

def start():
    port = 80
    hostname = os.environ['HTTP_HOST']
    if ':' in hostname:
        hostname, port = hostname.split(':')

    # This assumes the default text server_store is being used.
    # If you are not using that store, you'll need to change this.
    config['server_store'] = ['text', {'store_root': file_store_location}]
    config['server_prefix'] = web_server_base

    app = serve.load_app(hostname, port, config['urls_map'])
    BaseCGIHandler(sys.stdin, sys.stdout, sys.stderr, os.environ).run(app)

if __name__ == '__main__':
    start()
