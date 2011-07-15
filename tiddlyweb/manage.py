"""
Provide the workings for the twanager command line tool.
twanager calls handle() in this module and makes available
all commands that have been put into the COMMANDS dictionary
by the make_command() decorator.
"""

import logging
import os
import sys

from tiddlyweb.util import merge_config, std_error_message, initialize_logging


INTERNAL_PLUGINS = ['tiddlyweb.commands']

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
def usage(args):
    """List this help"""
    if args:
        std_error_message('ERROR: ' + args + '\n')
    for key in sorted(COMMANDS):
        std_error_message('%10s: %s' % (key, COMMANDS[key].description))
    sys.exit(1)


def handle(args):
    """
    Dispatch to the proper function for the command
    given in a args[1].
    """
    from tiddlyweb.config import config
    try:
        if args[1] == '--load':
            args = _external_load(args, config)
    except IndexError:
        args = []

    initialize_logging(config)

    plugins = INTERNAL_PLUGINS
    try:
        plugins.extend(config['twanager_plugins'])
        for plugin in plugins:
            logging.debug('attempting to import twanager plugin %s', plugin)
            # let the import fail with error if it does
            imported_module = __import__(plugin, {}, {}, ['init'])
            imported_module.init(config)
    except KeyError:
        pass  # no plugins

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
            logging.debug('running command %s with %s',
                    candidate_command, args)
            COMMANDS[candidate_command](args)
        except IndexError, exc:
            usage('Incorect number of arguments')
        except Exception, exc:
            if config.get('twanager.tracebacks', False):
                raise
            import traceback
            logging.error('twanager error with command "%s %s"\n%s',
                    candidate_command, args, traceback.format_exc())
            usage('%s: %s' % (exc.__class__.__name__, exc.args))
    else:
        usage('No matching command found')


def _external_load(args, config):
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
