"""
A grab bag of miscellaneous utility functions for TiddlyWeb that don't
fit in elsewhere.

Web specific utilities are in tiddlyweb.web.util.
"""

import logging
import codecs
import os
import sys

try:
    from hashlib import sha1
except ImportError:
    from sha import sha as sha1


class LockError(IOError):
    """
    This process was unable to get a lock.
    """
    pass


def merge_config(global_config, additional_config, reconfig=True):
    """
    Update the global_config with the additional data provided in
    the dict additional_config. If reconfig is True, then reread
    tiddlywebconfig.py so its overrides continue to operate.
    """
    for key in additional_config:
        try:
            # If this config item is a dict, update to
            # update it
            additional_config[key].keys()
            try:
                global_config[key].update(additional_config[key])
            except KeyError:
                global_config[key] = {}
                global_config[key].update(additional_config[key])
        except AttributeError:
            global_config[key] = additional_config[key]
    if reconfig:
        read_config(global_config)


def read_config(global_config):
    """
    Read in a local configuration override, called
    tiddlywebconfig.py, from the current working directory.
    If the file can't be imported an exception will be
    thrown, preventing unexpected results.

    What is expected in the override file is a dict with the
    name config.

    global_config is a reference to the currently operational
    main tiddlyweb config.
    """
    try:
        from tiddlywebconfig import config as custom_config
        merge_config(global_config, custom_config, reconfig=False)
    except ImportError, exc:
        if not exc.args[0].endswith('tiddlywebconfig'):
            raise  # error within tiddlywebconfig.py


def sha(data=''):
    """
    Centralize creation of sha digests, to
    manage deprecation of the sha module.
    """
    return sha1(data)


def binary_tiddler(tiddler):
    """
    Return true if this Tiddler has a 'type' which suggests the
    content of the tiddler is non-textual. This is usuallly used
    to determine if the tiddler should be base64 encoded.
    """
    return (tiddler.type and tiddler.type != 'None'
            and not pseudo_binary(tiddler.type))


def pseudo_binary(content_type):
    """
    Return true if the content type should be treated as a pseudo-binary.
    A pseudo binary is a type of textual content for which (this) TiddlyWeb
    (instance) has no serialization. TiddlyWeb requires that such content
    be uploaded encoded in UTF-8.
    """
    content_type = content_type.lower()
    return (content_type.startswith('text/')
            or content_type.endswith('+xml')
            or content_type.endswith('+json')
            or content_type == 'application/javascript'
            or content_type == 'application/json')


def read_utf8_file(filename):
    """
    Read a utf-8 encoded file.
    """
    source_file = codecs.open(filename, encoding='utf-8')
    content = source_file.read()
    source_file.close()
    return content


def renderable(tiddler, environ=None):
    """
    Return true if the provided tiddler's type is one
    that can be rendered by the wikitext render subsystem.
    """
    if not environ:
        environ = {}
    return (not tiddler.type
            or tiddler.type == 'None'
            or tiddler.type
                in environ.get('tiddlyweb.config', {}).get(
                    'wikitext.type_render_map', []))


def std_error_message(message):
    """
    Display a message on the stderr console.
    """
    try:
        print >> sys.stderr, message.encode('utf-8', 'replace')
    # there's a mismatch between our encoding and the output terminal
    except UnicodeDecodeError:
        try:
            print >> sys.stderr, message
        except UnicodeDecodeError:
            print >> sys.stderr, ('cannot display message due to '
                    'mismatching terminal character encoding')


def superclass_name(instance):
    """
    Given an instance return the lowerclass name of the penultimate
    class in the hierarchy (the last is object). This is used to do
    dynamic method lookups in adaptor classes via serializer.py and
    store.py while still allowing model entities to be subclassed.
    Those subclasses must insure that their __mro__ results in
    Bag, User, Recipe or Tiddler in the penultimate slot.
    """
    return instance.__class__.mro()[-2].__name__.lower()


def write_utf8_file(filename, content):
    """
    Write a string to utf-8 encoded file.
    """
    dest_file = codecs.open(filename, 'w', encoding='utf-8')
    dest_file.write(content)
    dest_file.close()


def write_lock(filename):
    """
    Make a lock file based on a filename.
    """

    lock_filename = _lock_filename(filename)

    if os.path.exists(lock_filename):
        pid = _read_lock_file(lock_filename)
        raise LockError('write lock for %s taken by %s' % (filename, pid))

    lock = open(lock_filename, 'w')
    pid = os.getpid()
    lock.write(str(pid))
    lock.close()


def write_unlock(filename):
    """
    Unlock the write lock.
    """
    lock_filename = _lock_filename(filename)
    os.unlink(lock_filename)


def initialize_logging(config, server=False):
    """
    Initialize the system logging. If run as twanager but there is
    no sub_command, don't log, otherwise do.
    """
    try:
        sub_command = sys.argv[1]
    except IndexError:
        sub_command = None
    if server or sub_command:
        _initialize_logging(config)


def abspath(path, config):
    """
    Adjust the given path so it is absolute.
    """
    if not os.path.isabs(path):
        root_dir = config.get('root_dir', '')
        path = os.path.join(root_dir, path)
    return path


def _initialize_logging(config):
    """
    Configure logging. If 'log_syslog' has a value it should point
    to a syslog facility to which we will log.

    Two loggers are established: 'tiddlyweb' and 'tiddlywebplugins'.
    Modules which wish to log should use `logging.getLogger(__name__)`
    to get a logger in the right part of the logging hierarchy.
    """
    syslog = config.get('log_syslog', None)

    logger = logging.getLogger('tiddlyweb')
    logger.propagate = False
    logger.setLevel(logging._levelNames[config['log_level']])

    plugin_logger = logging.getLogger('tiddlywebplugins')
    plugin_logger.propagate = False
    plugin_logger.setLevel(logging._levelNames[config['log_level']])

    if syslog:
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler(facility=syslog)
        formatter = logging.Formatter('%(levelname)s %(name)s: %(message)s')
        syslog_handler.setFormatter(formatter)
        logger.addHandler(syslog_handler)
        plugin_logger.addHandler(syslog_handler)
    else:
        from logging import FileHandler
        file_handler = FileHandler(
                filename=os.path.join(config['root_dir'], config['log_file']))
        formatter = logging.Formatter(
                '%(asctime)s %(levelname)s %(name)s: %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        plugin_logger.addHandler(file_handler)

    logger.debug('TiddlyWeb starting up as %s', sys.argv[0])


def _lock_filename(filename):
    """
    Return the pathname of the lock_filename.
    """
    pathname, basename = os.path.split(filename)
    lock_filename = os.path.join(pathname, '.%s' % basename)
    return lock_filename


def _read_lock_file(lockfile):
    """
    Read the pid from a the lock file.
    """
    lock = open(lockfile, 'r')
    pid = lock.read()
    lock.close()
    return pid
