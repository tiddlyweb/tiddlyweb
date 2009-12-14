"""
A collection of routines for doing things
like starting a server, creating a user,
importing a wiki, etc.
"""

import logging
import os
import sys

from tiddlyweb.config import config, merge_config
from tiddlyweb.store import Store, NoBagError
from tiddlyweb.serializer import Serializer
from tiddlyweb.model.user import User
from tiddlyweb.util import std_error_message

from tiddlyweb import __version__ as VERSION


INTERNAL_PLUGINS = []

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
def info(args):
    """Display info about TiddlyWeb."""
    print """This is TiddlyWeb version %s.
The current store is: %s.""" % (VERSION, config['server_store'][0])
    if config['system_plugins']:
        print 'System Plugins:'
        for plugin in config['system_plugins']:
            module = __import__(plugin)
            print '\t%s (%s)' % (plugin,
                    getattr(module, '__version__', 'unknown'))


@make_command()
def server(args):
    """Start the server using config settings. Provide <host name or IP number> <port> to override."""
    hostname = port = ''
    try:
        hostname, port = args[0:2]
    except(IndexError, ValueError), exc:
        if 0 < len(args) < 2:
            usage('you must include both a hostname or ip '
                'number and a port if using arguments: %s' % exc)
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
def userpass(args):
    """Change the password of an existing user. <username> <password>"""
    try:
        username, password = args[0:2]
    except (IndexError, ValueError), exc:
        usage('you must provide both a user and a password')

    try:
        store = _store()
        user = User(username)
        user = store.get(user)
        user.set_password(password)
        store.put(user)
    except Exception, exc:
        usage('unable to set password for user: %s' % exc)

    return True


@make_command()
def addrole(args):
    """Add a role to an existing user. <username> [role] [role] [role]"""
    try:
        username = args.pop(0)
        roles = args[0:]
    except (IndexError, ValueError), exc:
        usage('you must provide a user and at least one '
            'role: %s' % exc)

    try:
        store = _store()
        user = User(username)
        user = store.get(user)
        for role in roles:
            user.add_role(role)
        store.put(user)
    except Exception, exc:
        usage('unable to add role to user: %s' % exc)

    return True


@make_command()
def adduser(args):
    """Add or update a user to the database: <username> <password> [[role] [role] ...]"""
    try:
        username, password = args[0:2]
    except (IndexError, ValueError), exc:
        usage('you must include at least a username and password')

    try:
        roles = args[2:]
    except IndexError:
        roles = []

    # this will raise an except to be caught by the handler
    store = _store()
    user = User(username)
    user.set_password(password)
    for role in roles:
        user.add_role(role)
    store.put(user)

    return True


@make_command()
def recipe(args):
    """Create or update a recipe with the recipe text on stdin: <recipe>"""
    try:
        recipe_name = args[0]
    except IndexError, exc:
        usage('you must include a recipe name')

    from tiddlyweb.model.recipe import Recipe

    recipe = Recipe(recipe_name)

    content = sys.stdin.read()
    _put(recipe, unicode(content, 'UTF-8'), 'text')


@make_command()
def bag(args):
    """Create or update a bag with the json text on stdin: <bag>"""
    try:
        bag_name = args[0]
    except IndexError, exc:
        usage('you must include a bag name')

    from tiddlyweb.model.bag import Bag

    bag = Bag(bag_name)

    content = sys.stdin.read()
    if not len(content):
        content = '{"policy":{}}'
    _put(bag, unicode(content, 'UTF-8'), 'json')


@make_command()
def tiddler(args):
    """Import a single tiddler into an existing bag from stdin: <bag> <tiddler>"""
    try:
        bag_name, tiddler_name = args[0:3]
    except (IndexError, ValueError), exc:
        usage('you must include a tiddler and bag name')

    from tiddlyweb.model.tiddler import Tiddler

    tiddler = Tiddler(tiddler_name)
    tiddler.bag = bag_name

    content = sys.stdin.read()
    _put(tiddler, unicode(content, 'UTF-8'), 'text')


@make_command()
def lusers(args):
    """List all the users on the system"""
    store = _store()
    users = store.list_users()
    for user in users:
        user = store.get(user)
        print user.usersign, user.list_roles()


@make_command()
def lbags(args):
    """List all the bags on the system. [<bag> <bag> <bag>] to limit."""
    from tiddlyweb.model.bag import Bag
    store = _store()
    bags = [Bag(name) for name in args]
    if not bags:
        bags = store.list_bags()
    serializer = Serializer('json')
    for bag in bags:
        bag = store.get(bag)
        serializer.object = bag
        print 'Name: %s' % bag.name
        print serializer.to_string()
        print


@make_command()
def lrecipes(args):
    """List all the recipes on the system. [<recipe> <recipe> <recipe>] to limit."""
    from tiddlyweb.model.recipe import Recipe
    store = _store()
    recipes = [Recipe(name) for name in args]
    if not recipes:
        recipes = store.list_recipes()
    for recipe in recipes:
        recipe = store.get(recipe)
        print recipe.name, recipe.policy.owner
        for bag, filter in recipe.get_recipe():
            print '\t', bag, filter


@make_command()
def ltiddlers(args):
    """List all the tiddlers on the system. [<bag> <bag> <bag>] to limit."""
    from tiddlyweb.model.bag import Bag
    store = _store()
    bags = [Bag(name) for name in args]
    if not bags:
        bags = store.list_bags()
    try:
        for bag in bags:
            bag = store.get(bag)
            print bag.name, bag.policy.owner
            tiddlers = bag.list_tiddlers()
            for tiddler in tiddlers:
                tiddler = store.get(tiddler)
                print '  ', tiddler.title, tiddler.modifier
    except NoBagError, exc:
        usage('unable to inspect bag %s: %s' % (bag.name, exc))


@make_command()
def usage(*args):
    """List this help"""
    if args:
        std_error_message('ERROR: ' + ' '.join(args) + '\n')
    for key in sorted(COMMANDS):
        std_error_message('%10s: %s' % (key, COMMANDS[key].description))
    sys.exit(1)


def handle(args):
    """
    Dispatch to the proper function for the command
    given in a args[1].
    """
    try:
        if args[1] == '--load':
            args = _external_load(args)
    except IndexError:
        args = []

    plugins = INTERNAL_PLUGINS
    try:
        plugins.extend(config['twanager_plugins'])
        for plugin in plugins:
            logging.debug('attempting to import twanager plugin %s', plugin)
            # let the import fail with error if it does
            imported_module = __import__(plugin, {}, {}, ['init'])
            imported_module.init(config)
    except KeyError:
        pass # no plugins

    candidate_command = None
    try:
        candidate_command = args[1]
    except IndexError:
        usage('Missing command')

    try:
        args = args[2:]
    except IndexError:
        args = []

    if candidate_command and candidate_command in COMMANDS:
        try:
            logging.debug('running command %s with %s', candidate_command, args)
            COMMANDS[candidate_command](args)
        except IndexError, exc:
            usage('Incorect number of arguments')
        except Exception, exc:
            if config.get('twanager.tracebacks', False):
                raise
            import traceback
            logging.error('twanager error with command "%s %s"\n%s', candidate_command,
                    args, traceback.format_exc())
            usage('%s: %s' % (exc.__class__.__name__, exc.args))
    else:
        usage('No matching command found')


def _external_load(args):
    """
    Load a module from by request of the command line.
    """
    module = args[2]
    args = [args[0]] + args[3:]

    if module.endswith('.py'):
        path, module = os.path.split(module)
        module = module.replace('.py', '')
        sys.path.insert(0, path)
        imported_config = _import_module_config(module)
        sys.path.pop(0)
    else:
        imported_config = _import_module_config(module)

    merge_config(config, imported_config)

    return args


def _import_module_config(module):
    """
    Import the module named module to get at its config.
    """
    imported_module = __import__(module, {}, {}, ['config'])
    return imported_module.config


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
