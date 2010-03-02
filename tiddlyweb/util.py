"""
Miscellaneous utility functions for TiddlyWeb.
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
    except ImportError:
        pass # that's cool


def sha(data=''):
    """
    Centralize creation of sha digests, to
    manage deprecation of the sha module.
    """
    return sha1(data)


def read_utf8_file(filename):
    """
    Read a utf-8 encoded file.
    """
    source_file = codecs.open(filename, encoding='utf-8')
    content = source_file.read()
    source_file.close()
    return content


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
            print >> sys.stderr, 'cannot display message due to mismatching terminal character encoding'


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


def initialize_logging(config):
# Avoid writing a tiddlyweb.log under some circumstances
    try:
        try:
            current_command = sys.argv[0]
            current_sub_command = sys.argv[1]
        except IndexError:
            current_command = ''
            current_sub_command = ''
        # there's tiddlywebconfig.py here and it says log level is high, so log
        if config['log_level'] != 'INFO':
            raise IndexError
        # we're running the server so we want to log
        if 'twanager' in current_command and current_sub_command == 'server':
            raise IndexError
    except IndexError:
        logging.basicConfig(level=getattr(logging, config['log_level']),
                format='%(asctime)s %(levelname)-8s %(message)s',
                filename=os.path.join(config['root_dir'], config['log_file']))
        logging.debug('TiddlyWeb starting up as %s', sys.argv[0])


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
