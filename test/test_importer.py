"""
Test reading in a tiddler div via the importer.
"""

import sys
sys.path.append('.')

import html5lib
from html5lib import treebuilders


from tiddlyweb.config import config
from tiddlyweb.fromsvn import process_tiddler
from tiddlyweb.importer import handle_tiddler_div
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import Store

BAGNAME = 'test'
SAMPLE_BASIC_TIDDLER = """
<div title="GettingStarted">
<pre>To get started with this blank [[TiddlyWiki]], you'll need to modify the following tiddlers:
* [[SiteTitle ]] & [[SiteSubtitle]]: The title and subtitle of the site, as shown above (after saving, they will also appear in the browser title bar)
* [[MainMenu]]: The menu (usually on the left)
* [[DefaultTiddlers]]: Contains the names of the tiddlers that you want to appear when the TiddlyWiki is opened You'll also need to enter your username for signing your edits: <<option txtUserName>></pre>
</div>
"""

def setup_module(module):
    module.store = Store(config['server_store'][0], environ={'tiddlyweb.config': config})
    bag = Bag(BAGNAME)
    module.store.put(bag)

def test_import_simple_tiddler_div():
    div = _parse(SAMPLE_BASIC_TIDDLER)
    assert div['title'] == 'GettingStarted'

    handle_tiddler_div(BAGNAME, div, store)

    tiddler = Tiddler('GettingStarted', BAGNAME)
    tiddler = store.get(tiddler)
    assert tiddler.title == 'GettingStarted'
    assert 'as shown above (after' in tiddler.text

def test_from_svn_preprocessing():
    div = process_tiddler(SAMPLE_BASIC_TIDDLER)
    assert div['title'] == 'GettingStarted'
    assert '<<option txtUserName>>' in '%s' % div


def _parse(content):
    parser = html5lib.liberalxmlparser.XMLParser(tree=treebuilders.getTreeBuilder('beautifulsoup'))
    soup = parser.parseFragment(content)
    tiddler_div = soup.find('div')
    return tiddler_div


