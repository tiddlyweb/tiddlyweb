"""
This module provides a centralized collection of miscellaneous utility
functions used throughout TiddlyWeb and plugins.

Web specific utilities are in :py:mod:`tiddlyweb.web.util`.
"""

from __future__ import print_function

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
    Update the ``global_config`` with the additional data provided in
    the dict ``additional_config``. If ``reconfig`` is ``True``, then
    reread and merge ``tiddlywebconfig.py`` so its overrides continue
    to operate.

    Note that if the value of a existing key is a dict, then it is
    updated (merged) with the value from ``additional_config``.
    Otherwise the value is replaced.

    *Warning*: Please ensure (via tests) when using this that it will
    give the desired results.
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
    Read in a local configuration override, named ``tiddlywebconfig.py``,
    from the current working directory. If the file exists but can't be
    imported as valid Python an exception will be thrown, preventing
    unexpected results.

    What is expected in the override file is a dict with the name ``config``.

    ``global_config`` is a reference to the currently operational
    main TiddlyWeb :py:mod:`config <tiddlyweb.config>`. The read
    configuration data is merged into it.
    """
    try:
        from tiddlywebconfig import config as custom_config
        merge_config(global_config, custom_config, reconfig=False)
    except ImportError as exc:
        if not ('module named' in exc.args[0]
                and 'tiddlywebconfig' in exc.args[0]):
            raise  # error within tiddlywebconfig.py


def sha(data=''):
    """
    Create a sha1 digest of the ``data``.
    """
    return sha1(data.encode('UTF-8'))


def binary_tiddler(tiddler):
    """
    Test if a :py:class:`tiddler <tiddlyweb.model.tiddler.Tiddler>`
    represents binary content (e.g. an image).

    Return ``True`` if this Tiddler has a ``type`` which suggests the
    content of the tiddler is non-textual.
    """
    return (tiddler.type and tiddler.type != 'None'
            and not pseudo_binary(tiddler.type))


def pseudo_binary(content_type):
    """
    Test if a :py:class:`tiddler <tiddlyweb.model.tiddler.Tiddler>`
    represents textual content that should be treated as a pseudo-binary.

    A pseudo binary is defined as textual content for which (this) TiddlyWeb
    (instance) has no :py:class:`serialization
    <tiddlyweb.serializations.SerializationInterface>` or is not treated
    as :py:mod:`wikitext <tiddlyweb.wikitext>`. It is identified by a
    ``MIME`` type that looks like ``text``, ``json``, ``xml`` or
    ``javascript``.

    TiddlyWeb requires that such content be uploaded encoded as ``UTF-8``.
    """
    content_type = content_type.lower()
    return (content_type.startswith('text/')
            or content_type.endswith('+xml')
            or content_type.endswith('+json')
            or content_type == 'application/javascript'
            or content_type == 'application/json')


def read_utf8_file(filename):
    """
    Read the ``UTF-8`` encoded file at ``filename`` and return unicode.

    Allow any exceptions to raise.
    """
    with codecs.open(filename, encoding='utf-8') as source_file:
        content = source_file.read()
    return content


def renderable(tiddler, environ=None):
    """
    Return ``True`` if the provided :py:class:`tiddler's
    <tiddlyweb.model.tiddler.Tiddler>` ``type`` is one that can be
    rendered to HTML by the :py:mod:`wikitext <tiddlyweb.wikitext>`
    rendering subsystem.
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
    Display ``message`` on the ``stderr`` console.
    """
    print(message, file=sys.stderr)


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
    Write the unicode string in ``content`` to a ``UTF-8`` encoded
    file named ``filename``.

    Allow any exceptions to raise.
    """
    dest_file = codecs.open(filename, 'w', encoding='utf-8')
    dest_file.write(content)
    dest_file.close()


def write_lock(filename):
    """
    Create an advisory lock file based on ``filename``.

    This is primarily used by the :py:mod:`text store
    <tiddlyweb.stores.text>`.
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
    Unlock the write lock associated with ``filename``.
    """
    lock_filename = _lock_filename(filename)
    os.unlink(lock_filename)


def initialize_logging(config, server=False):
    """
    Initialize the system's logging.

    If this code is reached from ``twanager`` when there is no sub_command
    logging is not started. This avoids spurious ``tiddlyweb.log`` files
    popping up all over the place.
    """
    try:
        sub_command = sys.argv[1]
    except IndexError:
        sub_command = None
    if server or sub_command:
        _initialize_logging(config)


def _initialize_logging(config):
    """
    Configure logging.

    Two loggers are established: ``tiddlyweb`` and ``tiddlywebplugins``.
    Modules which wish to log should use ``logging.getLogger(__name__)``
    to get a logger in the right part of the logging hierarchy.
    """
    logger = logging.getLogger('tiddlyweb')
    logger.propagate = False
    logger.setLevel(logging._levelNames[config['log_level']])

    plugin_logger = logging.getLogger('tiddlywebplugins')
    plugin_logger.propagate = False
    plugin_logger.setLevel(logging._levelNames[config['log_level']])

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
    Return the pathname of the lock to used with ``filename``.
    """
    pathname, basename = os.path.split(filename)
    lock_filename = os.path.join(pathname, '.%s' % basename)
    return lock_filename


def _read_lock_file(lockfile):
    """
    Read the pid from the file named by ``lockfile``.
    """
    lock = open(lockfile, 'r')
    pid = lock.read()
    lock.close()
    return pid
