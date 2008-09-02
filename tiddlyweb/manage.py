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
        f.description = description
        commands[f.__name__] = f
        return f
    return decorate

@_make_command('Start the server: <hostname or ip number> <port>')
def server(args):
    try:
        hostname, port = args[0:2]
    except IndexError:
        help()
    except ValueError:
        help()

    from tiddlyweb.web import serve
    serve.start_cherrypy('./urls.map', hostname, int(port))

def _store():
    return Store(config['server_store'][0], environ={'tiddlyweb.config': config})

@_make_command('Add or update a user to the database: <username> <password> [[role] [role] ...]')
def adduser(args):
    try:
        username, password = args[0:2]
    except IndexError, e:
        help()
    except ValueError, e:
        help()

    roles = []
    try:
        roles = args[2:]
    except IndexError:
        pass

    try:
        store = _store()
        user = User(username)
        user.set_password(password)
        for role in roles:
            user.add_role(role)
        store.put(user)
    except Exception, e:
        print 'unable to create or update user: %s' % e
        raise

    return True

@_make_command('Import a Tiddlywiki html file into a bag: <filename> <bag name>')
def imwiki(args):
    from tiddlyweb.importer import import_wiki_file

    store = _store()

    try:
        filename, bag_name = args[0:2]
        import_wiki_file(store, filename, bag_name)
    except IndexError, e:
        print "index error: %s" % e
        help()
    except ValueError, e:
        print "value error: %s" % e
        help()

@_make_command('Create or update a recipe with the recipe text on stdin: <recipe name>')
def recipe(args):
    try:
        recipe_name = args[0]
    except IndexError:
        help()

    from tiddlyweb.recipe import Recipe
    from tiddlyweb.serializer import Serializer

    recipe = Recipe(recipe_name)

    content = _read_stdin()
    serializer = Serializer('text')
    serializer.object = recipe
    serializer.from_string(content)
    store = _store()
    store.put(recipe)

@_make_command('Create or update a bag with the json text on stdin: <bag name>')
def bag(args):
    try:
        bag_name = args[0]
    except IndexError:
        help()

    from tiddlyweb.bag import Bag
    from tiddlyweb.serializer import Serializer

    bag = Bag(bag_name)

    content = _read_stdin()
    if not len(content):
        content = '{"policy":{}}'
    serializer = Serializer('json')
    serializer.object = bag
    serializer.from_string(content)
    store = _store()
    store.put(bag)

@_make_command('Import a single tiddler into an existing bag from stdin: <tiddler_name> <bag name>')
def tiddler(args):
    try:
        tiddler_name, bag_name = args[0:3]
    except IndexError:
        help()
    except ValueError:
        help()

    from tiddlyweb.tiddler import Tiddler
    from tiddlyweb.serializer import Serializer

    tiddler = Tiddler(tiddler_name)
    tiddler.bag = bag_name

    content = _read_stdin()
    serializer = Serializer('text')
    serializer.object = tiddler
    serializer.from_string(content)
    store = _store()
    store.put(tiddler)

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

def _read_stdin():
    return sys.stdin.read()

