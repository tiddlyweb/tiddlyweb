"""
This is a sample of a module that runs TiddlyWeb 
under mod_python. What this script does is 
customize the TiddlyWeb application and then
provide that application (named application) as a
callable to a WSGI handler running under mod_python.

The required modpython_gateway can be found at
http://www.aminus.net/wiki/ModPythonGateway

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

You will need a custom tiddlywebconfig.py to
set some of the options used in this script.
'hostname' and 'server_prefix' being of particular import.

'server_prefix' would be set to '/twtest' in the example
above.
"""

import os
import os.path
import sys

os.environ['PYTHON_EGG_CACHE'] = '/tmp'

# chdir to the location of this running script so we have access 
# to tiddlywebconfig.py
dirname = os.path.dirname(__file__)
if dirname:
    os.chdir(dirname)

from tiddlyweb.web import serve

def start():
    app = serve.load_app()
    return app

# the mod_python wsgi handler will look for the callable 
# named application
application = start()
