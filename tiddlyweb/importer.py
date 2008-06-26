
import codecs
import re

from BeautifulSoup import BeautifulSoup

from tiddlyweb.web.serve import config
from tiddlyweb.store import Store
from tiddlyweb.tiddler import Tiddler

def import_wiki(filename='wiki', bagname='wiki'):
    f = codecs.open(filename, encoding='utf-8')
    wikitext = f.read()
    f.close()

    soup = BeautifulSoup(wikitext)
    store_area = soup.find('div', id='storeArea')
    divs = store_area.findAll('div')

    for tiddler in divs:
        _do_tiddler(bagname, tiddler)

def _do_tiddler(bagname, tiddler):
    new_tiddler = Tiddler(tiddler['title'], bag=bagname)

    new_tiddler.text = _html_decode(tiddler.find('pre').contents[0])

    for key in (['modifier', 'created', 'modified']):
        data = tiddler.get(key, None)
        if data:
            new_tiddler.__setattr__(key, data)
    new_tiddler.tags = _tag_string_to_list(tiddler.get('tags', ''))

    store = Store(config['server_store'][0])
    store.put(new_tiddler)

def _tag_string_to_list(string):
    tags = []
    tag_matcher = re.compile(r'([^ \]\[]+)|(?:\[\[([^\]]+)\]\])')
    for match in tag_matcher.finditer(string):
        if match.group(2):
            tags.append(match.group(2))
        elif match.group(1):
            tags.append(match.group(1))

    return tags

def _html_decode(text):
    return text.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&').replace('&quot;', '"')

