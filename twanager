#!/usr/bin/env python

import os
import sys

# extend module search path for access to tiddlywebconfig.py
cwd = os.getcwd()
sys.path.insert(0, cwd)
from tiddlyweb.manage import handle


if __name__ == '__main__':
    args = [unicode(arg, 'UTF-8') for arg in sys.argv]
    handle(args)
