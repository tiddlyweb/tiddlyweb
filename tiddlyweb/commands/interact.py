"""
interactive shell (REPL)
"""

import sys
import atexit
import code
import rlcompleter


def launch_shell(config, store, args):
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

    def complete(self, text, state):
        if not text:
            return ('    ', None)[state]
        else:
            return rlcompleter.Completer.complete(
                    self, text, state)
