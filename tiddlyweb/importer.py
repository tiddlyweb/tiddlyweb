"""
Given a string or file representing a wiki, do the
work to import it into a named bag.
"""

import codecs

import html5lib
from html5lib import treebuilders

from tiddlyweb.model.tiddler import Tiddler, string_to_tags_list


def import_wiki_file(store, filename='wiki', bagname='wiki'):
    """
    Read a wiki in a file and import all the tiddlers into a bag.
    """
    wikifile = codecs.open(filename, encoding='utf-8', errors='replace')
    wikitext = wikifile.read()
    wikifile.close()
    return import_wiki(store, wikitext, bagname)


def import_wiki(store, wikitext, bagname='wiki'):
    """
    Import the wiki provided as a string and import all the tiddlers
    into a bag.
    """
    parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder('beautifulsoup'))
    soup = parser.parse(wikitext)
    store_area = soup.find('div', id='storeArea')
    divs = store_area.findAll('div')

    for tiddler_div in divs:
        handle_tiddler_div(bagname, tiddler_div, store)


def handle_tiddler_div(bagname, tiddler_div, store):
    """
    Create a new Tiddler from a tiddler div, in beautifulsoup
    form.
    """
    new_tiddler = Tiddler(tiddler_div['title'], bag=bagname)

    try:
        new_tiddler.text = _html_decode(tiddler_div.find('pre').contents[0])
    except IndexError:
        # there are no contents in the tiddler
        new_tiddler.text = ''

    for attr, value in tiddler_div.attrs:
        data = tiddler_div.get(attr, None)
        if data and attr != 'tags':
            if attr in (['modifier', 'created', 'modified']):
                new_tiddler.__setattr__(attr, data)
            else:
                new_tiddler.fields[attr] = data
    new_tiddler.tags = _tag_string_to_list(tiddler_div.get('tags', ''))

    try:
        store.put(new_tiddler)
    except OSError, exc:
        # This tiddler has a name that we can't yet write to the
        # store. For now we just state the error and carry on.
        import sys
        print >> sys.stderr, 'Unable to write %s: %s' % (new_tiddler.title, exc)


def _tag_string_to_list(string):
    """
    Turn a string of tags in TiddlyWiki format into a list.
    """
    return string_to_tags_list(string)


def _html_decode(text):
    """
    Decode HTML entities used in TiddlyWiki content into the 'real' things.
    """
    return text.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&').replace('&quot;', '"')
