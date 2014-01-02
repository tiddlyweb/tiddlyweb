"""
This is a handler for running tiddlyweb under web servers that can be
configured to host an Python module as a WSGI application. Such servers
include apache2 using mod_wsgi, or nginx using uwsgi.

This file has also been used with Passenger: http://www.modrails.com/

The hosted module provides a global named 'application'.

##################################################
For mod_wsgi

Your apache must be configured to use mod_wsgi.

Add the following to server config (this is a real virtual host,
the names have been changed...):

<VirtualHost *>
    ServerName barney.example.com
    AllowEncodedSlashes On
    Alias /static /home/barney/public_html/barney.example.com/static
    <Directory /home/barney/public_html/barney.example.com/static>
        Order allow,deny
        Allow from all
    </Directory>
    ErrorLog /var/log/apache2/barney.example.com-error.log
    CustomLog /var/log/apache2/barney.example.com-access.log combined
    WSGIDaemonProcess barney.example.com user=barney processes=1 threads=10
    WSGIProcessGroup barney.example.com
    WSGIPassAuthorization On
    WSGIScriptAlias /wiki /home/barney/tiddlywebs/barney.example.com/wsgiapp.py
</VirtualHost>

Replace barney.example.com with the hostname being used.
Replace barney with the user the process should run as.
Replace /wiki with the prefix to the tiddlyweb (often just '/').
Replace the path after /wiki with the path to apache.py which
    should live in in the tiddlyweb instance directory.

If you wish to use the http_basic extractor when using
mod_wsgi, you need to set

    WSGIPassAuthorization On

in the apache configuration.

For more mod_wsgi configuration info see:

    http://code.google.com/p/modwsgi/wiki/ConfigurationDirectives

##################################################

Information on using nginx and uwsgi can be found at:

    http://tiddlyweb.tiddlyspace.com/Using%20nginx%20and%20uwsgi
    http://tsdbup.tiddlyspace.com/WorkingNginxConfig

##################################################

In tiddlywebconfig.py:

    set server_prefix to the prefix above (/wiki)
    set server_host to the scheme, hostname and port being used
    set css_uri to a css file if you have one

server_host is a complex data structure as follows:

    'server_host': {
        'scheme': 'http',
        'host': 'some.example.com',
        'port': '80',
    }

##################################################

If you are using Passenger, thus far the only 
testing has been with Dreamhosts setup. For that
rename wsgiapp.py to passenger_wsgi.py and configure
as described here:

    http://wiki.dreamhost.com/Passenger_WSGI
"""

import os
import sys

# If on a hosting service with Passenger and you want to
# use a custom Python, you may uncomment the following. Change
# INTERP to your preferred Python.
#INTERP = "/home/osmosoft/bin/python"
#if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

# you may wish to change this path
# It can also be controlled from mod_wsgi config.
os.environ['PYTHON_EGG_CACHE'] = '/tmp'

def start():
    dirname = os.path.dirname(__file__)
    if sys.path[0] != dirname:
        sys.path.insert(0, dirname)
    from tiddlyweb.web import serve
    app = serve.load_app(app_prefix='', dirname=dirname)
    return app

# web server code will look for a callable named application
application = start()
