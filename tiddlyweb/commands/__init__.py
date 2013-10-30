"""
Command line tools for TiddlyWeb are accessed via the ``twanager``
script. Each command is named by the first argument passed to the
script.

The commands defined in this package are added to a list of available
commands using the ``twanager`` plugin mechanism.  That list is extensible
via ``twanager_plugins`` in :py:mod:`tiddlyweb.config` and
:py:func:`tiddlyweb.manage.make_command`.

Typical commands do things like starting a server, creating a user and
listing existing entities.
"""

from __future__ import print_function

import sys

from tiddlyweb.store import Store, NoBagError
from tiddlyweb.serializer import Serializer
from tiddlyweb.model.user import User

from tiddlyweb.manage import make_command, usage

from tiddlyweb import __version__ as VERSION

from tiddlyweb.fixups import unicode


def init(config):
    """
    Establish the commands during ``twanager`` startup.
    """

    @make_command()
    def info(args):
        """Display info about TiddlyWeb."""
        print("""This is TiddlyWeb version %s.
    The current store is: %s.""" % (VERSION, config['server_store'][0]))
        if config['system_plugins']:
            print('System Plugins:')
            for plugin in config['system_plugins']:
                module = __import__(plugin)
                print('\t%s (%s)' % (plugin,
                        getattr(module, '__version__', 'unknown')))

    @make_command()
    def server(args):
        """Start the server using config settings. Provide <host name or IP number> <port> to override."""
        hostname = port = ''
        try:
            hostname, port = args[0:2]
        except(IndexError, ValueError) as exc:
            if 0 < len(args) < 2:
                usage('you must include both a hostname or ip '
                    'number and a port if using arguments: %s' % exc)
            else:
                pass

        if hostname and port:
            config['server_host'] = {
                    'scheme': 'http',
                    'host': str(hostname),
                    'port': str(port),
            }
        server_module = config.get('wsgi_server', 'tiddlyweb.web.serve')
        imported_module = __import__(server_module, {}, {}, ['start_server'])
        imported_module.start_server(config)

    @make_command()
    def userpass(args):
        """Change the password of an existing user. <username> <password>"""
        try:
            username, password = args[0:2]
        except (IndexError, ValueError) as exc:
            usage('you must provide both a user and a password')

        try:
            store = _store()
            user = User(username)
            user = store.get(user)
            user.set_password(password)
            store.put(user)
        except Exception as exc:
            usage('unable to set password for user: %s' % exc)

        return True

    @make_command()
    def addrole(args):
        """Add a role to an existing user. <username> [role] [role] [role]"""
        try:
            username = args.pop(0)
            roles = args[0:]
        except (IndexError, ValueError) as exc:
            usage('you must provide a user and at least one '
                'role: %s' % exc)

        try:
            store = _store()
            user = User(username)
            user = store.get(user)
            for role in roles:
                user.add_role(role)
            store.put(user)
        except Exception as exc:
            usage('unable to add role to user: %s' % exc)

        return True

    @make_command()
    def adduser(args):
        """Add or update a user to the database: <username> <password> [[role] [role] ...]"""
        try:
            username, password = args[0:2]
        except (IndexError, ValueError):
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
        except IndexError:
            usage('you must include a recipe name')

        from tiddlyweb.model.recipe import Recipe

        new_recipe = Recipe(recipe_name)

        content = sys.stdin.read()
        _put(new_recipe, unicode(content, 'UTF-8'), 'text')

    @make_command()
    def bag(args):
        """Create or update a bag with the json text on stdin: <bag>"""
        try:
            bag_name = args[0]
        except IndexError:
            usage('you must include a bag name')

        from tiddlyweb.model.bag import Bag

        new_bag = Bag(bag_name)

        content = sys.stdin.read()
        if not len(content):
            content = '{"policy":{}}'
        _put(new_bag, unicode(content, 'UTF-8'), 'json')

    @make_command()
    def tiddler(args):
        """Import a single tiddler into an existing bag from stdin: <bag> <tiddler>"""
        try:
            bag_name, tiddler_name = args[0:3]
        except (IndexError, ValueError):
            usage('you must include a tiddler and bag name')

        from tiddlyweb.model.tiddler import Tiddler

        new_tiddler = Tiddler(tiddler_name)
        new_tiddler.bag = bag_name

        content = sys.stdin.read()
        _put(new_tiddler, unicode(content, 'UTF-8'), 'text')

    @make_command()
    def lusers(args):
        """List all the users on the system. [<user> <user> <user>] to limit."""
        store = _store()
        users = [User(name) for name in args]
        if not users:
            users = store.list_users()
        for user in users:
            user = store.get(user)
            print(user.usersign, ', '.join(role
                    for role in user.list_roles()))

    @make_command()
    def lbags(args):
        """List all the bags on the system. [<bag> <bag> <bag>] to limit."""
        from tiddlyweb.model.bag import Bag
        store = _store()
        bags = [Bag(name) for name in args]
        if not bags:
            bags = store.list_bags()
        serializer = Serializer('json')
        for listed_bag in bags:
            listed_bag = store.get(listed_bag)
            serializer.object = listed_bag
            print('Name:', listed_bag.name)
            print(serializer.to_string())
            print()

    @make_command()
    def lrecipes(args):
        """List all the recipes on the system. [<recipe> <recipe> <recipe>] to limit."""
        from tiddlyweb.model.recipe import Recipe
        store = _store()
        recipes = [Recipe(name) for name in args]
        if not recipes:
            recipes = store.list_recipes()
        for listed_recipe in recipes:
            listed_recipe = store.get(listed_recipe)
            owner = listed_recipe.policy.owner or ''
            print(listed_recipe.name, owner)
            for recipe_bag, recipe_filter in listed_recipe.get_recipe():
                print('\t', recipe_bag, recipe_filter)

    @make_command()
    def ltiddlers(args):
        """List all the tiddlers on the system. [<bag> <bag> <bag>] to limit."""
        from tiddlyweb.model.bag import Bag
        store = _store()
        bags = [Bag(name) for name in args]
        if not bags:
            bags = store.list_bags()
        try:
            for listed_bag in bags:
                listed_bag = store.get(listed_bag)
                owner = listed_bag.policy.owner or ''
                print(listed_bag.name, owner)
                tiddlers = store.list_bag_tiddlers(listed_bag)
                for listed_tiddler in tiddlers:
                    print('\t%s' % listed_tiddler.title)
        except NoBagError as exc:
            usage('unable to inspect bag %s: %s' % (listed_bag.name, exc))

    @make_command()
    def interact(args):
        """Enter a Python interactive shell."""
        from tiddlyweb.commands.interact import launch_shell
        launch_shell(config, _store(), args)
        sys.exit(0)  # XXX: should be handled by `make_command`

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
                config['server_store'][1],
                environ={'tiddlyweb.config': config})
