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
by the web server. Set file_store_location (below) to the
path to this directory.

You will need to set server_prefix and server_host in the
tiddlywebconfig.py in the instance directory that you create.

See http://tiddlyweb.peemore.com for general documentation and
http://bengillies.net/.a/#%5B%5BRunning%20on%20TiddlyWeb%2C%20Part%20One%5D%5D
for an installation tutorial, specifically for people who
do not have root access on their server.
"""

import os
import sys

from wsgiref.handlers import BaseCGIHandler
from tiddlyweb.web import serve
from tiddlyweb.config import config

# Where the content is stored.
# It is best to make this somewhere other than
# the directory where the CGI is running.
file_store_location = '/tmp/store'

def start():
    # This assumes the default text server_store is being used.
    # If you are not using that store, you'll need to change this.
    config['server_store'] = ['text', {'store_root': file_store_location}]
    app = serve.load_app()
    BaseCGIHandler(sys.stdin, sys.stdout, sys.stderr, os.environ).run(app)

if __name__ == '__main__':
    start()
