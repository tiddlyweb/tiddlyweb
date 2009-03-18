"""
Miscellaneous utility functions for TiddlyWeb.
"""

import os

class LockError(IOError):
    """
    This process was unable to get a lock.
    """
    pass


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
