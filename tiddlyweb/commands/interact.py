"""
This module provides a ``twanager`` command ``interact`` which
provides a Python shell preloaded with the necessary local
variables to interact with the current instance's :py:class:`store
<tiddlyweb.store.Store>` and the entities within. The locals are:

* :py:class:`Recipe <tiddlyweb.model.recipe.Recipe>`
* :py:class:`Bag <tiddlyweb.model.bag.Bag>`
* :py:class:`Tiddler <tiddlyweb.model.tiddler.Tiddler>`
* :py:class:`User <tiddlyweb.model.user.User>`
* :py:class:`Policy <tiddlyweb.model.policy.Policy>`
* :py:class:`Serializer <tiddlyweb.serializer.Serializer>`
* :py:mod:`control <tiddlyweb.control>`
* :py:mod:`util <tiddlyweb.util>`
* :py:mod:`web <tiddlyweb.web.util>`
* An ``environ`` containing ``tiddlyweb.config`` and
  `tiddlyweb.store`` keys and values.
* A ``config`` containing the current ``tiddlyweb.config``.

These are enough to do most operations.
"""

import sys
import atexit
import code
import rlcompleter


def launch_shell(config, store, args):
    """
    Establish the basic environment for the shell and then start it.
    """
    # make basic API elements available within the REPL context
    from tiddlyweb.model.recipe import Recipe
    from tiddlyweb.model.bag import Bag
    from tiddlyweb.model.policy import Policy
    from tiddlyweb.model.tiddler import Tiddler
    from tiddlyweb.model.user import User
    from tiddlyweb.serializer import Serializer
    from tiddlyweb import control
    from tiddlyweb import util
    from tiddlyweb.web import util as web

    environ = {
        'tiddlyweb.config': config,
        'tiddlyweb.store': store
    }
    _locals = locals()
    _locals['config'] = config

    TiddlyWebREPL(locals=_locals).interact()


# See
# http://stackoverflow.com/questions/4031135/why-does-my-python-interactive-console-not-work-properly
# and
# http://stackoverflow.com/questions/7116038/python-tab-completion-mac-osx-10-7-lion
# for the details on tab completion
class TiddlyWebREPL(code.InteractiveConsole):
    """
    An interactive console for the current TiddlyWeb instance.

    This augments it's super class by adding tab completion and
    establishing a set of useful local variables.
    """

    def __init__(self, locals=None, filename="<console>"):
        code.InteractiveConsole.__init__(self, locals, filename)
        try:
            import readline
        except ImportError:
            pass
        else:
            try:
                readline.set_completer(TabCompleter(locals).complete)
            except ImportError:
                pass

            if 'libedit' in readline.__doc__:
                readline.parse_and_bind("bind -e")
                readline.parse_and_bind("bind '\t' rl_complete")
            else:
                readline.parse_and_bind("tab: complete")

            # history file support
            histfile = '.twihistory'
            try:
                readline.read_history_file(histfile)
            except IOError:
                pass
            atexit.register(readline.write_history_file, histfile)
            del histfile


class TabCompleter(rlcompleter.Completer):
    """
    Tab completion for the interactive shell that allows pressing
    the tab character to indicate an indent.
    """

    def complete(self, text, state):
        """
        Complete the provided ``text``. If there is no text, indent.
        """
        if not text:
            return ('    ', None)[state]
        else:
            return rlcompleter.Completer.complete(
                    self, text, state)
