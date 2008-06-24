"""
A collection of routines for doing things
like starting a server, creating a user,
importing a wiki, etc.
"""

import sys
import os

from tiddlyweb.web.serve import config
from tiddlyweb.store import Store
from tiddlyweb.user import User

commands = {}

def _make_command(description):
    def decorate(f):
        global commands
        f.manage_command = True
        f.description = description
        commands[f.__name__] = f
        return f
    return decorate

@_make_command('Start the server: <host or ip name> <port>')
def server(args):
    try:
        hostname, port = args[0:2]
    except IndexError:
        help()
    except ValueError:
        help()

    from tiddlyweb.web import serve
    from test import fixtures
    if not os.path.exists(fixtures.textstore.store_dirname):
        fixtures.reset_textstore()
        store = Store('text')
        fixtures.muchdata(store)
    serve.start_cherrypy('./urls.map', hostname, int(port))

@_make_command('Add or update a user to the database: <username> <password>')
def adduser(args):
    try:
        username, password = args[0:2]
    except IndexError, e:
        help()
    except ValueError, e:
        help()

    try:
        store = Store(config['server_store'])
        user = User(username)
        user.set_password(password)
        store.put(user)
    except Exception, e:
        print 'unable to create or update user: %s' % e
        raise

    return True

@_make_command('Import a Tiddlywiki html file into a bag: <filename> <bag name>')
def imwiki(args):
    print 'import args is: %s' % args

@_make_command('Create or update a recipe with the text on stdin: <recipe name>')
def recipe(args):
    print 'recipe args is: %s' % args

@_make_command('Create or update a bag with the text on stdin: <bag name>')
def bag(args):
    print 'bag args is: %s' % args

@_make_command('List this help')
def help(*args):
    for key in sorted(commands):
        print "%s\t\t%s" % (key, commands[key].description)
    sys.exit(0)

def handle(args):
    try:
        candidate_command = args[1]
    except IndexError:
        help([])

    try:
        args = args[2:]
    except IndexError:
        args = []

    if candidate_command in commands:
        commands[candidate_command](args)
    else:
        help(args)

