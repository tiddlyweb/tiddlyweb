"""
A collection of routines for doing things
like starting a server, creating a user,
importing a wiki, etc.
"""

import logging
import sys

from tiddlyweb.web.serve import config
from tiddlyweb.store import Store
from tiddlyweb.serializer import Serializer
from tiddlyweb.model.user import User

INTERNAL_PLUGINS = ['tiddlyweb.fromsvn', 'tiddlyweb.instancer']

COMMANDS = {}


def make_command():
    """
    A decorator that marks the decorated method
    as a member of the commands dictionary, with
    associated help.
    """

    def decorate(func):
        """
        Add the function to the commands dictionary.
        """
        func.description = func.__doc__
        COMMANDS[func.__name__] = func
        return func
    return decorate


@make_command()
def server(args):
    """Start the server: <host name or IP number> <port>"""
    hostname = port = ''
    try:
        hostname, port = args[0:2]
    except(IndexError, ValueError), exc:
        if 0 < len(args) < 2:
            print >> sys.stderr, "you must include both a hostname or ip number and a " \
                "port if using arguments: %s" % exc
            usage()
        else:
            pass

    if hostname and port:
        config['server_host'] = {
                'scheme': 'http',
                'host': hostname,
                'port': port,
                }

    from tiddlyweb.web import serve
    serve.start_cherrypy()


@make_command()
def adduser(args):
    """Add or update a user to the database: <username> <password> [[role] [role] ...]"""
    try:
        username, password = args[0:2]
    except (IndexError, ValueError), exc:
        print >> sys.stderr, "you must include at least a username and password: %s" % exc
        usage()

    try:
        roles = args[2:]
    except IndexError:
        roles = []

    try:
        store = _store()
        user = User(username)
        user.set_password(password)
        for role in roles:
            user.add_role(role)
        store.put(user)
    except Exception, exc:
        print >> sys.stderr, 'unable to create or update user: %s' % exc
        raise

    return True


@make_command()
def imwiki(args):
    """Import a Tiddlywiki html file into a bag: <filename> <bag>"""
    from tiddlyweb.importer import import_wiki_file

    store = _store()

    try:
        filename, bag_name = args[0:2]
        import_wiki_file(store, filename, bag_name)
    except IndexError, exc:
        print >> sys.stderr, "index error: %s" % exc
        usage()
    except ValueError, exc:
        print >> sys.stderr, "value error: %s" % exc
        usage()


@make_command()
def recipe(args):
    """Create or update a recipe with the recipe text on stdin: <recipe>"""
    try:
        recipe_name = args[0]
    except IndexError, exc:
        print >> sys.stderr, "you must include a recipe name: %s" % exc
        usage()

    from tiddlyweb.model.recipe import Recipe

    recipe = Recipe(recipe_name)

    content = sys.stdin.read()
    _put(recipe, content, 'text')


@make_command()
def bag(args):
    """Create or update a bag with the json text on stdin: <bag>"""
    try:
        bag_name = args[0]
    except IndexError, exc:
        print >> sys.stderr, "you must include a bag name: %s" % exc
        usage()

    from tiddlyweb.model.bag import Bag

    bag = Bag(bag_name)

    content = sys.stdin.read()
    if not len(content):
        content = '{"policy":{}}'
    _put(bag, content, 'json')


@make_command()
def tiddler(args):
    """Import a single tiddler into an existing bag from stdin: <tiddler> <bag>"""
    try:
        tiddler_name, bag_name = args[0:3]
    except (IndexError, ValueError), exc:
        print >> sys.stderr, "you must include a tiddler and bag name: %s" % exc
        usage()

    from tiddlyweb.model.tiddler import Tiddler

    tiddler = Tiddler(tiddler_name)
    tiddler.bag = bag_name

    content = sys.stdin.read()
    _put(tiddler, content, 'text')


@make_command()
def usage(*args):
    """List this help"""
    for key in sorted(COMMANDS):
        print >> sys.stderr, "%10s: %s" % (key, COMMANDS[key].description)
    sys.exit(1)


def handle(args):
    """
    Dispatch to the proper function for the command
    given in a args[1].
    """
    plugins = INTERNAL_PLUGINS
    try:
        plugins.extend(config['twanager_plugins'])
        for plugin in plugins:
            logging.debug('attempting to import twanager plugin %s' % plugin)
            # let the import fail with error if it does
            imported_module = __import__(plugin, {}, {}, ['init'])
            imported_module.init(config)
    except KeyError:
        pass # no plugins

    candidate_command = None
    try:
        candidate_command = args[1]
    except IndexError:
        usage([])

    try:
        args = args[2:]
    except IndexError:
        args = []

    if candidate_command and candidate_command in COMMANDS:
        try:
            logging.debug('running command %s with %s' % (candidate_command, args))
            COMMANDS[candidate_command](args)
        except IndexError, exc:
            print >> sys.stderr, "Incorect number of arguments: %s" % exc
            usage()
        except IOError, exc:
            print >> sys.stderr, "IOError: %s" % exc
            usage()
    else:
        usage(args)

def _put(entity, content, serialization):
    """
    Put entity to store, by serializing content
    using the named serialization.
    """
    serializer = Serializer(serialization)
    serializer.object = entity
    serializer.from_string(content)
    _store().put(entity)


def _store():
    """Get our Store from config."""
    return Store(config['server_store'][0],
            environ={'tiddlyweb.config': config})

