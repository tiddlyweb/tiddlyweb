"""
Demonstration debug plugin.

When the web application is loaded config['system_plugins']
is checked for a list of string representing modules in sys.path.

For each of those plugins we call init() on it, and pass in
the config dict. The init method may then do whatever it
likes, such as overriding methods in other packages, or updating
data structures or otherwise having a good ol time. Not
exactly sure what yet.
"""

from tiddlyweb.filter import FILTER_MAP


def init(config):

    # here's an example of extending the filtering
    # system. It counts the letter i in tiddler.text.

    def i_counter(argument, tiddlers):
        return [tiddler for tiddler in tiddlers if tiddler.text.count('i') >= int(argument)]

    FILTER_MAP['i'] = i_counter
