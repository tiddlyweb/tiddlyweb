"""
This is a handler for running tiddlyweb 
under mod_wsgi. Add the following to 
server config (in a virtual host section):

    WSGIDaemonProcess teamtasks.peermore.com user=cdent processes=2 threads=15
    WSGIProcessGroup teamtasks.peermore.com
    WSGIScriptAlias /t /home/cdent/public_html/teamtasks.peermore.com/mod_wsgi.py

Replace teamtasks.peermore.com with the hostname being used.
Replace cdent with the user the process should run as. Remove
    the user line if you want to use the apache user.
Replace /t with the prefix to the tiddlyweb (can be / but
    then all requests will go to the mod_wsgi.py script).
Replace the path after /t with the path to mod_wsgi.py which 
    should live in in the tiddlyweb instance directory.

In tiddlywebconfig.py:

    set server_prefix to the prefix above (/t)
    set hostname to the hostname being used
    set css_uri to a css file if you have one
"""

import os
import os.path
import sys

# chdir to the location of this running script so we have access 
# to tiddlywebconfig.py
dirname = os.path.dirname(__file__)
if dirname:
    os.chdir(dirname)

os.environ['PYTHON_EGG_CACHE'] = '/tmp'
sys.path.extend(dirname)

from tiddlyweb.web import serve

def start():
    app = serve.load_app()
    return app

# the mod_python wsgi handler will look for the callable 
# named application
application = start()
