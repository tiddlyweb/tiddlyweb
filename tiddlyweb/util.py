"""
Miscellaneous utility functions for TiddlyWeb.
"""

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
