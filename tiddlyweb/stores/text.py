"""
A text-based StorageInterface that stores entities
in the filesystem.
"""

import codecs
import logging
import os
import simplejson
import shutil
import time
import urllib

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import Policy
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.user import User
from tiddlyweb.serializer import Serializer
from tiddlyweb.store import NoBagError, NoRecipeError, NoTiddlerError, \
        NoUserError, StoreLockError, StoreEncodingError
from tiddlyweb.stores import StorageInterface
from tiddlyweb.util import LockError, write_lock, write_unlock, \
        read_utf8_file, write_utf8_file


class Store(StorageInterface):
    """
    A StorageInterface which stores text-based representations
    in a collection of directories and files.
    """

    def __init__(self, store_config=None, environ=None):
        super(Store, self).__init__(store_config, environ)
        self.serializer = Serializer('text')
        self._root = self._fixup_root(store_config['store_root'])
        self._init_store()

    def _fixup_root(self, path):
        """
        Adjust the store_root path so it is absolute.

        This is required in some web serving environments.
        """
        if not os.path.isabs(path):
            path = os.path.join(self.environ['tiddlyweb.config'].
                    get('root_dir', ''), path)
        return path

    def _init_store(self):
        """
        Make sure the data storage directory and
        structure is present.
        """
        if not os.path.exists(self._store_root()):
            os.mkdir(self._store_root())
            for name in ['bags', 'recipes', 'users']:
                path = os.path.join(self._store_root(), name)
                if not os.path.exists(path):
                    os.mkdir(path)

    def recipe_delete(self, recipe):
        """
        Remove a recipe, irrevocably, from the system.
        No impact on tiddlers.
        """
        try:
            recipe_path = self._recipe_path(recipe)
            if not os.path.exists(recipe_path):
                raise NoRecipeError('%s not present' % recipe_path)
            os.remove(recipe_path)
        except (NoRecipeError, StoreEncodingError), exc:
            raise NoRecipeError(exc)
        except Exception, exc:
            raise IOError('unable to delete recipe %s: %s' %
                    (recipe.name, exc))

    def recipe_get(self, recipe):
        """
        Read a recipe from the store.
        """
        try:
            recipe_path = self._recipe_path(recipe)
            self.serializer.object = recipe
            recipe_string = read_utf8_file(recipe_path)
        except StoreEncodingError, exc:
            raise NoRecipeError(exc)
        except IOError, exc:
            raise NoRecipeError('unable to get recipe %s: %s' %
                    (recipe.name, exc))

        return self.serializer.from_string(recipe_string)

    def recipe_put(self, recipe):
        """
        Put a recipe into the store.
        """
        try:
            recipe_path = self._recipe_path(recipe)
            self.serializer.object = recipe
            write_utf8_file(recipe_path, self.serializer.to_string())
        except StoreEncodingError, exc:
            raise NoRecipeError(exc)

    def bag_delete(self, bag):
        """
        Delete a bag AND THE TIDDLERS WITHIN from
        the system.
        """
        bag_path = self._bag_path(bag.name)

        try:
            if not os.path.exists(bag_path):
                raise NoBagError('%s not present' % bag_path)
            shutil.rmtree(bag_path)
        except NoBagError:
            raise
        except Exception, exc:
            raise IOError('unable to delete bag %s: %s' % (bag.name, exc))

    def bag_get(self, bag):
        """
        Read a bag from the store and get a list
        of its tiddlers.
        """
        bag_path = self._bag_path(bag.name)

        try:
            bag.desc = self._read_bag_description(bag_path)
            bag.policy = self._read_policy(bag_path)
        except IOError, exc:
            raise NoBagError(
                    'unable to read policy or description at %s: %s' %
                    (bag_path, exc))

        return bag

    def bag_put(self, bag):
        """
        Put a bag into the store, writing its
        name, description and policy.
        """
        bag_path = self._bag_path(bag.name)
        tiddlers_dir = self._tiddlers_dir(bag.name)

        if not os.path.exists(bag_path):
            os.mkdir(bag_path)

        if not os.path.exists(tiddlers_dir):
            os.mkdir(tiddlers_dir)

        self._write_bag_description(bag.desc, bag_path)
        self._write_policy(bag.policy, bag_path)

    def tiddler_delete(self, tiddler):
        """
        Irrevocably remove a tiddler and its directory.
        """
        try:
            tiddler_base_filename = self._tiddler_base_filename(tiddler)
            if not os.path.exists(tiddler_base_filename):
                raise NoTiddlerError('%s not present' % tiddler_base_filename)
            shutil.rmtree(tiddler_base_filename)
        except NoTiddlerError:
            raise
        except Exception, exc:
            raise IOError('unable to delete %s: %s' % (tiddler.title, exc))

    def tiddler_get(self, tiddler):
        """
        Get a tiddler as string from a bag and deserialize it into
        object.
        """
        try:
            # read in the desired tiddler
            tiddler = self._read_tiddler_revision(tiddler)
            # now make another tiddler to get created time
            # base_tiddler is the head of the revision stack
            base_tiddler = Tiddler(tiddler.title)
            base_tiddler.bag = tiddler.bag
            base_tiddler = self._read_tiddler_revision(base_tiddler, index=-1)
            # set created on new tiddler from modified on base_tiddler
            # (might be the same)
            tiddler.created = base_tiddler.modified
            tiddler.creator = base_tiddler.modifier
            return tiddler
        except IOError, exc:
            raise NoTiddlerError('no tiddler for %s: %s' %
                    (tiddler.title, exc))

    def tiddler_put(self, tiddler):
        """
        Write a tiddler into the store. We only write if
        the bag already exists. Bag creation is a
        separate action from writing to a bag.
        """
        tiddler_base_filename = self._tiddler_base_filename(tiddler)
        if not os.path.exists(tiddler_base_filename):
            try:
                os.mkdir(tiddler_base_filename)
            except OSError, exc:
                raise NoTiddlerError('unable to put tiddler: %s' % exc)

        locked = 0
        lock_attempts = 0
        while (not locked):
            try:
                lock_attempts = lock_attempts + 1
                write_lock(tiddler_base_filename)
                locked = 1
            except LockError, exc:
                if lock_attempts > 4:
                    raise StoreLockError(exc)
                time.sleep(.1)

        # Protect against incoming tiddlers that have revision
        # set. Since we are putting a new one, we want the system
        # to calculate.
        tiddler.revision = None
        revision = self._tiddler_revision_filename(tiddler) + 1
        tiddler_filename = self._tiddler_full_filename(tiddler, revision)

        self.serializer.object = tiddler
        write_utf8_file(tiddler_filename, self.serializer.to_string())
        write_unlock(tiddler_base_filename)
        tiddler.revision = revision

    def user_delete(self, user):
        """
        Delete a user from the store.
        """
        try:
            user_path = self._user_path(user)
            if not os.path.exists(user_path):
                raise NoUserError('%s not present' % user_path)
            os.unlink(user_path)
        except NoUserError:
            raise
        except Exception, exc:
            raise IOError('unable to delete %s: %s' % (user.usersign, exc))

    def user_get(self, user):
        """
        Read a user from the store.
        """
        try:
            user_path = self._user_path(user)
            user_info = read_utf8_file(user_path)
            user_data = simplejson.loads(user_info)
            for key, value in user_data.items():
                if key == 'roles':
                    user.roles = set(value)
                    continue
                if key == 'password':
                    key = '_password'
                user.__setattr__(key, value)
            return user
        except IOError, exc:
            raise NoUserError('unable to get user %s: %s' %
                    (user.usersign, exc))

    def user_put(self, user):
        """
        Put a user data into the store.
        The user's information is store as JSON,
        for ease.
        """
        user_path = self._user_path(user)
        user_dict = {}
        for key in ['usersign', 'note', '_password', 'roles']:
            value = user.__getattribute__(key)
            if key == 'roles':
                user_dict[key] = list(value)
                continue
            if key == '_password':
                key = 'password'
            user_dict[key] = value
        user_info = simplejson.dumps(user_dict, indent=0)
        write_utf8_file(user_path, user_info)

    def list_recipes(self):
        """
        List all the recipes in the store.
        """
        path = os.path.join(self._store_root(), 'recipes')
        recipes = self._files_in_dir(path)

        return (Recipe(urllib.unquote(recipe).decode('utf-8'))
                for recipe in recipes)

    def list_bags(self):
        """
        List all the bags in the store.
        """
        bags = self._bag_filenames()

        return (Bag(urllib.unquote(bag).decode('utf-8')) for bag in bags)

    def list_bag_tiddlers(self, bag):
        """
        List all the tiddlers in the provided bag.
        """
        tiddlers_dir = self._tiddlers_dir(bag.name)

        try:
            tiddlers = (filename for filename
                    in self._files_in_dir(tiddlers_dir)
                    if os.path.isdir(os.path.join(tiddlers_dir, filename)))
        except (IOError, OSError), exc:
            raise NoBagError('unable to list tiddlers in bag: %s' % exc)
        for title in tiddlers:
            title = urllib.unquote(title).decode('utf-8')
            tiddler = Tiddler(title, bag.name)
            yield tiddler

    def list_users(self):
        """
        List all the users in the store.
        """
        path = os.path.join(self._store_root(), 'users')
        users = self._files_in_dir(path)

        return (User(urllib.unquote(user).decode('utf-8')) for user in users)

    def list_tiddler_revisions(self, tiddler):
        """
        List all the revisions of one tiddler,
        returning a list of ints.
        """
        tiddler_base_filename = self._tiddler_base_filename(tiddler)
        try:
            revisions = sorted(
                    int(x) for x in
                        self._numeric_files_in_dir(tiddler_base_filename))
        except OSError, exc:
            raise NoTiddlerError('unable to list revisions in tiddler: %s'
                    % exc)
        revisions.reverse()
        return revisions

    def search(self, search_query):
        """
        Search in the store for tiddlers that match search_query.
        This is intentionally simple, slow and broken to encourage overriding.
        """
        bag_filenames = self._bag_filenames()

        query = search_query.lower()

        for bagname in bag_filenames:
            bagname = urllib.unquote(bagname).decode('utf-8')
            tiddler_dir = self._tiddlers_dir(bagname)
            tiddler_files = self._files_in_dir(tiddler_dir)
            for tiddler_name in tiddler_files:
                tiddler = Tiddler(
                        title=urllib.unquote(tiddler_name).decode('utf-8'),
                        bag=bagname)
                try:
                    revision_id = self.list_tiddler_revisions(tiddler)[0]
                    if query in tiddler.title.lower():
                        yield tiddler
                        continue
                    tiddler_file = codecs.open(
                        self._tiddler_full_filename(tiddler, revision_id),
                        encoding='utf-8')
                    for line in tiddler_file:
                        if query in line.lower():
                            yield tiddler
                            break
                except (OSError, NoTiddlerError), exc:
                    logging.warn('malformed tiddler during search: %s:%s',
                            bagname, tiddler_name)
        return

    def _bag_filenames(self):
        """
        List the filenames that are bags.
        """
        path = os.path.join(self._store_root(), 'bags')
        return self._files_in_dir(path)

    def _bag_path(self, bag_name):
        """
        Return a string that is the path to a bag.
        """
        try:
            return os.path.join(self._store_root(), 'bags',
                    _encode_filename(bag_name))
        except (AttributeError, StoreEncodingError), exc:
            raise NoBagError('No bag name: %s' % exc)

    def _files_in_dir(self, path):
        """
        List the filenames in a dir that do not start with .
        """
        return (x for x in os.listdir(path))

    def _numeric_files_in_dir(self, path):
        """
        List the filename in a dir that are not made up of
        digits.
        """
        return (x for x in self._files_in_dir(path) if x.isdigit())

    def _read_tiddler_file(self, tiddler, tiddler_filename):
        """
        Read a tiddler file from the disk, returning
        a tiddler object.
        """
        tiddler_string = read_utf8_file(tiddler_filename)
        self.serializer.object = tiddler
        tiddler = self.serializer.from_string(tiddler_string)
        return tiddler

    def _read_tiddler_revision(self, tiddler, index=0):
        """
        Read a specific revision of a tiddler from disk.
        """
        tiddler_base_filename = self._tiddler_base_filename(tiddler)
        tiddler_revision = self._tiddler_revision_filename(tiddler,
                index=index)
        tiddler_filename = self._tiddler_full_filename(tiddler,
                tiddler_revision)
        tiddler = self._read_tiddler_file(tiddler, tiddler_filename)
        tiddler.revision = tiddler_revision
        return tiddler

    def _read_bag_description(self, bag_path):
        """
        Read and return the description of a bag.
        """
        desc_filename = os.path.join(bag_path, 'description')
        if not os.path.exists(desc_filename):
            return ''
        desc = read_utf8_file(desc_filename)
        return desc

    def _read_policy(self, bag_path):
        """
        Read and return a bag's policy file,
        return the Policy object.
        """
        policy_filename = os.path.join(bag_path, 'policy')
        policy = read_utf8_file(policy_filename)
        policy_data = simplejson.loads(policy)
        policy = Policy()
        for key, value in policy_data.items():
            policy.__setattr__(key, value)
        return policy

    def _recipe_path(self, recipe):
        """
        Return a string representing the pathname of a recipe.
        """
        return os.path.join(self._store_root(), 'recipes',
                _encode_filename(recipe.name))

    def _store_root(self):
        """
        Return a string which is the path to the root of the store.
        """
        return self._root

    def _tiddler_base_filename(self, tiddler):
        """
        Return the string that is the pathname to
        a tiddler's directory.
        """
        # should we get a Bag or a name here?
        bag_name = tiddler.bag

        store_dir = self._tiddlers_dir(bag_name)

        if not os.path.exists(store_dir):
            raise NoBagError('%s does not exist' % store_dir)

        try:
            return os.path.join(store_dir, _encode_filename(tiddler.title))
        except StoreEncodingError, exc:
            raise NoTiddlerError(exc)

    def _tiddler_full_filename(self, tiddler, revision):
        """
        Return the full path to the respective tiddler file.
        """
        return os.path.join(self._tiddlers_dir(tiddler.bag),
            _encode_filename(tiddler.title), str(revision))

    def _tiddlers_dir(self, bag_name):
        """
        Return the string that is the pathname of the
        tiddlers directory in a bag.
        """
        return os.path.join(self._bag_path(bag_name), 'tiddlers')

    def _tiddler_revision_filename(self, tiddler, index=0):
        """
        Calculate the revision filename for the tiddler revision
        we want.
        """
        revision = 0
        if tiddler.revision:
            revision = tiddler.revision
        else:
            revisions = self.list_tiddler_revisions(tiddler)
            if revisions:
                revision = revisions[index]
        return int(revision)

    def _user_path(self, user):
        """
        Return the pathname for a user in the store.
        """
        return os.path.join(self._store_root(), 'users',
                _encode_filename(user.usersign))

    def _write_bag_description(self, desc, bag_path):
        """
        Write the description of a bag to disk.
        """
        desc_filename = os.path.join(bag_path, 'description')
        write_utf8_file(desc_filename, desc)

    def _write_policy(self, policy, bag_path):
        """
        Write the policy of a bad to disk.
        """
        policy_dict = {}
        for key in Policy.attributes:
            policy_dict[key] = policy.__getattribute__(key)
        policy_string = simplejson.dumps(policy_dict)
        policy_filename = os.path.join(bag_path, 'policy')
        write_utf8_file(policy_filename, policy_string)


def _encode_filename(filename):
    """
    utf-8 encode, then url escape, some filename,
    making it easy to use on various filesystems.

    Also check for no ../ in filenames.
    """

    if not filename or '../' in filename:
        raise StoreEncodingError('invalid name for entity')
    return urllib.quote(filename.encode('utf-8'), safe='')
