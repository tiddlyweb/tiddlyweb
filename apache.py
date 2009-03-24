"""
This is a handler for running tiddlyweb
under apache using either mod_wsgi or mod_python.

mod_wsgi is a better choice.

##################################################
For mod_wsgi

Your apache must be configured to use mod_wsgi.

Add the following to server config (in a virtual host section)

    WSGIDaemonProcess teamtasks.peermore.com user=cdent processes=2 threads=15
    WSGIProcessGroup teamtasks.peermore.com
    WSGIScriptAlias /peerwiki /home/cdent/public_html/teamtasks.peermore.com/apache.py

Replace teamtasks.peermore.com with the hostname being used.
Replace cdent with the user the process should run as. Remove
    the user=cdent part if you want to run as the the apache user.
Replace /peerwiki with the prefix to the tiddlyweb.
Replace the path after /peerwiki with the path to apache.py which
    should live in in the tiddlyweb instance directory.

If you wish to use the http_basic extractor when using
mod_wsgi, you need to set

    WSGIPassAuthorization On

in the apache configuration.

##################################################
For mod_python

Your apache must be configured with mod_python.

What this script does is provide a callable
(named application) to a WSGI handler running under
mod_python.

A gateway from mod_python to WSGI is required
it can be found at
http://www.aminus.net/wiki/ModPythonGateway

Adjust the apache configuration something like
the following:

        <Location /peerwiki>
                PythonPath "['/home/cdent/www/peerwiki'] + sys.path"
                PythonOption SCRIPT_NAME /peerwiki
                SetHandler python-program
                PythonHandler modpython_gateway::handler
                PythonOption wsgi.application apache::application
        </Location>

In your own setup the name twtest and the path to it
would need to be changed.

##################################################
For both

In tiddlywebconfig.py:

    set server_prefix to the prefix above (/peerwiki)
    set server_host to the scheme, hostname and port being used
    set css_uri to a css file if you have one

server_host is a complex data structure as follows:

    'server_host': {
        'scheme': 'http',
        'host': 'some.example.com',
        'port': '80',
    }

"""

import os
import sys

# chdir to the location of this running script so we have access
# to tiddlywebconfig.py and plugins
dirname = os.path.dirname(__file__)
if dirname:
    os.chdir(dirname)

# you may wish to change this path
os.environ['PYTHON_EGG_CACHE'] = '/tmp'
sys.path.insert(0, dirname)

from tiddlyweb.web import serve


def start():
    app = serve.load_app()
    return app

# apache code will look for a callable # named application
application = start()
