"""
This is a handler for running tiddlyweb
under apache using either mod_wsgi or mod_python.

Of those two, mod_wsgi is a better choice.

This file has also been used with Passenger:
http://www.modrails.com/

There are configuration variables to set after
this docstring.

##################################################
For mod_wsgi

Your apache must be configured to use mod_wsgi.

Add the following to server config (this is a real virtual host,
the name have been changed...):

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
    WSGIScriptAlias /wiki /home/barney/tiddlywebs/barney.example.com/apache.py
</VirtualHost>

Replace barney.example.com with the hostname being used.
Replace barney with the user the process should run as.
Replace /wiki with the prefix to the tiddlyweb.
Replace the path after /wiki with the path to apache.py which
    should live in in the tiddlyweb instance directory.

If you wish to use the http_basic extractor when using
mod_wsgi, you need to set

    WSGIPassAuthorization On

in the apache configuration.

In WSGIScriptAlias you may use just / for the path, but it
can result in challenges for hosting other things on the same
VirtualHost.

For more mod_wsgi configuration info see:

    http://code.google.com/p/modwsgi/wiki/ConfigurationDirectives

##################################################
For mod_python

Your apache must be configured with mod_python.

What this script does is provide a callable
(named application) to a WSGI handler running under
mod_python.

A gateway from mod_python to WSGI is required
it can be found at:

    http://www.aminus.net/wiki/ModPythonGateway

Adjust your apache configuration similar to the following:

        <Location /wiki>
                PythonPath "['/home/barney/www/wiki'] + sys.path"
                PythonOption SCRIPT_NAME /wiki
                SetHandler python-program
                PythonHandler modpython_gateway::handler
                PythonOption wsgi.application apache::application
        </Location>

In your own setup the name wiki and the path to it
would need to be changed.

##################################################
For both

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
rename apache.py to passenger_wsgi.py and configure
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

# web server code will look for a callable # named application
application = start()
