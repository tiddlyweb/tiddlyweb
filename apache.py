"""
This file is placed in an instance directory, and 
then calls tiddlyweb.web.apache to do the work. Look
in that file for configuration information.
"""
import os
from tiddlyweb.web.apache import start
dirname = os.path.dirname(__file__)
application = start(dirname)
