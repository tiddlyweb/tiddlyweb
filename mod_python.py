"""
This is a sample of a module that runs TiddlyWeb 
under mod_python. What this script does is 
customize the TiddlyWeb application and then
provide that application (named application) as a
callable to a WSGI handler running under mod_python.

modpython_gateway can be found at
http://www.aminus.net//wiki/ModPythonGateway

(There are other options as well if you are stuck
with mod_python. If you are not but wish to use
Apache, mod_wsgi is a better choice.)

The apache configuration has something like this:

        <Location /twtest>
                PythonPath "['/home/cdent/www/twtest'] + sys.path"
                PythonOption SCRIPT_NAME /twtest
                SetHandler python-program
                PythonHandler modpython_gateway::handler
                PythonOption wsgi.application mod_python::application
        </Location>

For purposes beyond this script the name twtest and
the path to it would need to be changed.

Instead of setting config items in this script a
tiddlywebconfig.py could be used instead.

You will need to fill in values for some of the
variables below.
"""

import os
import os.path
import sys

# Change this to the location of the tiddlyweb code,
# if tiddlyweb is not in sys.path
sys.path.append('/home/cdent/www/twtest/TiddlyWeb')

from tiddlyweb.web import serve
from tiddlyweb.config import config

# Where is the TiddlyWeb content stored
file_store_location = '/home/cdent/www/twtest/TiddlyWeb/docstore'

def start():
    # What is our hostname
    hostname = 'plugins.tiddlywiki.org'

    # What is path to us (the base url)
    server_prefix = '/twtest'

    port = 80
    if ':' in hostname:
        hostname, port = hostname.split(':')

    # This assumes the default text server_store is being used.
    # If you are not using that store, you'll need to change this.
    config['server_store'] = ['text', {'store_root': file_store_location}]
    config['server_prefix'] = server_prefix

    app = serve.load_app(hostname, port, config['urls_map'])
    return app

# chdir to the location of this running script so we have access 
# urls.map and lib/empty.html
os.chdir(os.path.dirname(__file__))

# the mod_python wsgi handler will look for the callable 
# named application
application = start()
