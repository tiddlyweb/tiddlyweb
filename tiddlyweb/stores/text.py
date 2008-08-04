"""
Simple functions for storing stuff as textfiles
on the filesystem.
"""

import os
import codecs
import time
import simplejson
import shutil

from tiddlyweb.bag import Bag, Policy
from tiddlyweb.recipe import Recipe
from tiddlyweb.tiddler import Tiddler
from tiddlyweb.serializer import Serializer
from tiddlyweb.store import NoBagError, NoRecipeError, NoTiddlerError, NoUserError, StoreLockError
from tiddlyweb.stores import StorageInterface

class Store(StorageInterface):

    def recipe_get(self, recipe):
        recipe_path = self._recipe_path(recipe)

        try:
            recipe_file = codecs.open(recipe_path, encoding='utf-8')
            serializer = Serializer('text')
            serializer.object = recipe
            recipe_string = recipe_file.read()
            recipe_file.close()
        except IOError, e:
            raise NoRecipeError, 'unable to get recipe %s: %s' % (recipe.name, e)

        return serializer.from_string(recipe_string)

    def recipe_put(self, recipe):
        recipe_path = self._recipe_path(recipe)

        recipe_file = codecs.open(recipe_path, 'w', encoding='utf-8')

        serializer = Serializer('text')
        serializer.object = recipe

        recipe_file.write(serializer.to_string())

        recipe_file.close()

    def bag_get(self, bag):
        bag_path = self._bag_path(bag.name)
        tiddlers_dir = self._tiddlers_dir(bag.name)

        try:
            tiddlers = self._files_in_dir(tiddlers_dir)
        except OSError, e:
            raise NoBagError, 'unable to list tiddlers in bag: %s' % e
        for tiddler in tiddlers:
            bag.add_tiddler(Tiddler(title=tiddler))

        bag.desc = self._read_bag_description(bag_path)
        bag.policy = self._read_policy(bag_path)

        return bag

    def bag_put(self, bag):
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
                raise NoTiddlerError, '%s not present' % tiddler_base_filename
            shutil.rmtree(tiddler_base_filename)
        except NoTiddlerError:
            raise
        except Exception, e:
            raise IOError, 'unable to delete %s: %s' % (tiddler.title, e)

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
            # set created on new tiddler from modified on base_tiddler (might be the same)
            tiddler.created = base_tiddler.modified
            return tiddler
        except IOError, e:
            raise NoTiddlerError, 'no tiddler for %s: %s' % (tiddler.title, e)

    def tiddler_put(self, tiddler):
        """
        Write a tiddler into the store. We only write if
        the bag already exists. Bag creation is a 
        separate action from writing to a bag.

        XXX: This should be in a try with a finally?
        """

        tiddler_base_filename = self._tiddler_base_filename(tiddler)
        if not os.path.exists(tiddler_base_filename):
            os.mkdir(tiddler_base_filename)
        locked = 0
        lock_attempts = 0
        while (not locked):
            try:
                lock_attempts = lock_attempts + 1
                self.write_lock(tiddler_base_filename)
                locked = 1
            except StoreLockError, e:
                if lock_attempts > 4:
                    raise StoreLockError, e
                time.sleep(.1)

        revision = self._tiddler_revision_filename(tiddler) + 1
        tiddler_filename = os.path.join(tiddler_base_filename, '%s' % revision)
        tiddler_file = codecs.open(tiddler_filename, 'w', encoding='utf-8')

        serializer = Serializer('text')
        serializer.object = tiddler

        tiddler_file.write(serializer.to_string())

        self.write_unlock(tiddler_base_filename)
        tiddler.revision = revision
        tiddler_file.close()
        self.tiddler_written(tiddler)

    def user_get(self, user):
        user_path = self._user_path(user)

        try:
            user_file = codecs.open(user_path, encoding='utf-8')
            user_info = user_file.read()
            user_file.close()
            user_data = simplejson.loads(user_info)
            for key, value in user_data.items():
                if key == 'password':
                    key = '_password'
                user.__setattr__(key, value)
            return user
        except IOError, e:
            raise NoUserError, 'unable to get user %s: %s' % (user.usersign, e)

    def user_put(self, user):
        user_path = self._user_path(user)

        user_file = codecs.open(user_path, 'w', encoding='utf-8')
        user_dict = {}
        for key in ['usersign', 'note', '_password']:
            value = user.__getattribute__(key)
            if key == '_password':
                key = 'password'
            user_dict[key] = value
        user_info = simplejson.dumps(user_dict, indent=0)
        user_file.write(user_info)
        user_file.close()

    def list_recipes(self):
        path = os.path.join(self._store_root(), 'recipes')
        recipes = self._files_in_dir(path)

        return [Recipe(recipe.decode('utf-8')) for recipe in recipes]

    def list_bags(self):
        path = os.path.join(self._store_root(), 'bags')
        bags = self._files_in_dir(path)

        return [Bag(bag.decode('utf-8')) for bag in bags]

    def list_tiddler_revisions(self, tiddler):
        tiddler_base_filename = self._tiddler_base_filename(tiddler)
        try: 
            revisions = sorted([int(x) for x in self._files_in_dir(tiddler_base_filename)])
        except OSError, e:
            raise NoTiddlerError, 'unable to list revisions in tiddler: %s' % e
        revisions.reverse()
        return revisions

    def search(self, search_query):
        """
        Search in the store for tiddlers that match search_query.
        This is intentionally simple, slow and broken to encourage overriding.
        """
        path = os.path.join(self._store_root(), 'bags')
        bags = self._files_in_dir(path)
        found_tiddlers = []

        query = search_query.lower()

        for bagname in bags:
            tiddler_dir = os.path.join(self._store_root(), 'bags', bagname, 'tiddlers')
            tiddler_files = self._files_in_dir(tiddler_dir)
            for tiddler_name in tiddler_files:
                tiddler = Tiddler(title=tiddler_name.decode('utf-8'),bag=bagname.decode('utf-8'))
                revision_id = self.list_tiddler_revisions(tiddler)[0]
                try:
                    tiddler_file = open(os.path.join(tiddler_dir, tiddler_name, str(revision_id)))
                    for line in tiddler_file:
                        if query in line.lower():
                            found_tiddlers.append(tiddler)
                            break
                except OSError, e:
                    raise NoTiddlerError, 'unable to list revisions in tiddler: %s' % e
        return found_tiddlers

    def write_lock(self, filename):
        """
        Make a lock file based on a filename.
        """

        lock_filename = self._lock_filename(filename)

        if os.path.exists(lock_filename):
            pid = self._read_lock_file(lock_filename)
            raise StoreLockError, 'write lock for %s taken by %s' % (filename, pid)

        lock = open(lock_filename, 'w')
        pid = os.getpid()
        lock.write(str(pid))
        lock.close

    def write_unlock(self, filename):
        """
        Unlock the write lock.
        """
        lock_filename = self._lock_filename(filename)
        os.unlink(lock_filename)

    def _bag_path(self, bag_name):
        try:
            return os.path.join(self._store_root(), 'bags', bag_name)
        except AttributeError, e:
            raise NoBagError, 'No bag name: %s' % e

    def _files_in_dir(self, path):
        return filter(lambda x: not x.startswith('.'), os.listdir(path))

    def _lock_filename(self, filename):
        pathname, basename = os.path.split(filename)
        lock_filename = os.path.join(pathname, '.%s' % basename)
        return lock_filename

    def _read_lock_file(self, lockfile):
        lock = open(lockfile, 'r')
        pid = lock.read()
        lock.close()
        return pid

    def _read_tiddler_file(self, tiddler, tiddler_filename):
        tiddler_file = codecs.open(tiddler_filename, encoding='utf-8')
        serializer = Serializer('text')
        serializer.object = tiddler
        tiddler_string = tiddler_file.read()
        tiddler_file.close()
        tiddler = serializer.from_string(tiddler_string)
        return tiddler

    def _read_tiddler_revision(self, tiddler, index=0):
        tiddler_base_filename = self._tiddler_base_filename(tiddler)
        tiddler_revision = self._tiddler_revision_filename(tiddler, index=index)
        tiddler_filename = os.path.join(tiddler_base_filename, str(tiddler_revision))
        tiddler = self._read_tiddler_file(tiddler, tiddler_filename)
        tiddler.revision = tiddler_revision
        return tiddler

    def _read_bag_description(self, bag_path):
        desc_filename = os.path.join(bag_path, 'description')
        if not os.path.exists(desc_filename):
            return ''
        desc_file = codecs.open(desc_filename, encoding='utf-8')
        desc = desc_file.read()
        desc_file.close()
        return desc

    def _read_policy(self, bag_path):
        policy_filename = os.path.join(bag_path, 'policy')
        policy_file = codecs.open(policy_filename, encoding='utf-8')
        policy = policy_file.read()
        policy_file.close()
        policy_data = simplejson.loads(policy)
        policy = Policy()
        for key, value in policy_data.items():
            policy.__setattr__(key, value)
        return policy

    def _recipe_path(self, recipe):
        return os.path.join(self._store_root(), 'recipes', recipe.name)

    def _store_root(self):
        return self.environ['tiddlyweb.config']['server_store'][1]['store_root']

    def _tiddler_base_filename(self, tiddler):
        # should be get a Bag or a name here?
        bag_name = tiddler.bag

        store_dir = self._tiddlers_dir(bag_name)

        if not os.path.exists(store_dir):
            raise NoBagError, "%s does not exist" % store_dir

        return os.path.join(store_dir, tiddler.title)

    def _tiddlers_dir(self, bag_name):
        return os.path.join(self._bag_path(bag_name), 'tiddlers')

    def _tiddler_revision_filename(self, tiddler, index=0):
        revision = 0
        if tiddler.revision:
            revision = tiddler.revision
        else:
            revisions = self.list_tiddler_revisions(tiddler)
            if revisions:
                revision = revisions[index]
        return int(revision)

    def _user_path(self, user):
        return os.path.join(self._store_root(), 'users', user.usersign)

    def _write_bag_description(self, desc, bag_path):
        desc_filename = os.path.join(bag_path, 'description')
        self._write_string_to_file(desc_filename, desc)

    def _write_policy(self, policy, bag_path):
        policy_dict = {}
        for key in ['read','write','create','delete','manage','owner']:
            policy_dict[key] = policy.__getattribute__(key)
        policy_string = simplejson.dumps(policy_dict)
        policy_filename = os.path.join(bag_path, 'policy')
        self._write_string_to_file(policy_filename, policy_string)

    def _write_string_to_file(self, filename, content):
        dest_file = codecs.open(filename, 'w', encoding='utf-8')
        dest_file.write(content)
        dest_file.close()

