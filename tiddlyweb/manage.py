"""
A collection of routines for doing things
like starting a server, creating a user,
importing a wiki, etc.
"""

import sys

from tiddlyweb.web.serve import config
from tiddlyweb.store import Store
from tiddlyweb.user import User

COMMANDS = {}

def _make_command():
    """
    A decorator that marks the decorated method
    as a member of the commands dictionary, with
    associated help.
    """
    def decorate(func):
        """
        Add the function to the commands dictionary.
        """
        global COMMANDS
        func.description = func.__doc__
        COMMANDS[func.__name__] = func
        return func
    return decorate

@_make_command()
def server(args):
    """Start the server: <hostname or ip number> <port>"""
    try:
        hostname, port = args[0:2]
    except IndexError:
        usage()
    except ValueError:
        usage()

    from tiddlyweb.web import serve
    serve.start_cherrypy(config['urls_map'], hostname, int(port))

def _store():
    """Get our Store from config."""
    return Store(config['server_store'][0], environ={'tiddlyweb.config': config})

@_make_command()
def adduser(args):
    """Add or update a user to the database: <username> <password> [[role] [role] ...]"""
    try:
        username, password = args[0:2]
    except (IndexError, ValueError), exc:
        usage()

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
    except Exception, exc:
        print 'unable to create or update user: %s' % exc
        raise

    return True

@_make_command()
def imwiki(args):
    """Import a Tiddlywiki html file into a bag: <filename> <bag name>"""
    from tiddlyweb.importer import import_wiki_file

    store = _store()

    try:
        filename, bag_name = args[0:2]
        import_wiki_file(store, filename, bag_name)
    except IndexError, exc:
        print "index error: %s" % exc
        usage()
    except ValueError, exc:
        print "value error: %s" % exc
        usage()

@_make_command()
def recipe(args):
    """Create or update a recipe with the recipe text on stdin: <recipe name>"""
    try:
        recipe_name = args[0]
    except IndexError:
        usage()

    from tiddlyweb.recipe import Recipe
    from tiddlyweb.serializer import Serializer

    recipe = Recipe(recipe_name)

    content = sys.stdin.read()
    serializer = Serializer('text')
    serializer.object = recipe
    serializer.from_string(content)
    store = _store()
    store.put(recipe)

@_make_command()
def bag(args):
    """Create or update a bag with the json text on stdin: <bag name>"""
    try:
        bag_name = args[0]
    except IndexError:
        usage()

    from tiddlyweb.bag import Bag
    from tiddlyweb.serializer import Serializer

    bag = Bag(bag_name)

    content = sys.stdin.read()
    if not len(content):
        content = '{"policy":{}}'
    serializer = Serializer('json')
    serializer.object = bag
    serializer.from_string(content)
    store = _store()
    store.put(bag)

@_make_command()
def tiddler(args):
    """Import a single tiddler into an existing bag from stdin: <tiddler_name> <bag name>"""
    try:
        tiddler_name, bag_name = args[0:3]
    except (IndexError, ValueError):
        usage()

    from tiddlyweb.tiddler import Tiddler
    from tiddlyweb.serializer import Serializer

    tiddler = Tiddler(tiddler_name)
    tiddler.bag = bag_name

    content = sys.stdin.read()
    serializer = Serializer('text')
    serializer.object = tiddler
    serializer.from_string(content)
    store = _store()
    store.put(tiddler)

@_make_command()
def usage(*args):
    """List this help"""
    for key in sorted(COMMANDS):
        print "%s\t\t%s" % (key, COMMANDS[key].description)
    sys.exit(0)

def handle(args):
    """
    Dispatch to the proper function for the command
    given in a args[1].
    """
    try:
        candidate_command = args[1]
    except IndexError:
        usage([])

    try:
        args = args[2:]
    except IndexError:
        args = []

    if candidate_command in COMMANDS:
        COMMANDS[candidate_command](args)
    else:
        usage(args)
