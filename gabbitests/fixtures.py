
import os
from shutil import rmtree
from tempfile import mkdtemp
from string import lowercase

from gabbi.fixture import GabbiFixture

from tiddlyweb.model.bag import Bag
from tiddlyweb.config import config
from tiddlyweb.store import Store

class TempInstance(GabbiFixture):

    def start_fixture(self):
        """Establish an instance for this suite of tests.

        Make the instance dir
        cd into it
        ought to be enough
        """
        self.tempdir = mkdtemp(prefix='tiddlyweb')
        self.old_cwd = os.getcwd()
        os.chdir(self.tempdir)

    def stop_fixture(self):
        """Destroy the tempdir."""
        os.chdir(self.old_cwd)
        if not os.environ.get('TIDDLYWEB_TEST_PRESERVE'):
            rmtree(self.tempdir)


class MondoData(GabbiFixture):
    """Create some data in the current instances.

    Depends on TempInstance.
    """

    def start_fixture(self):
        store = get_store(config)
        for letter in lowercase:
            bag = Bag(letter)
            store.put(bag)

    def stop_fixture(self):
        """No cleanup required, TempInstance will get that."""
        pass


def get_store(config):
    return Store(config['server_store'][0], config['server_store'][1],
                 {'tiddlyweb.config': config})
