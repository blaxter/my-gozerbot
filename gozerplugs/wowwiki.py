# plugs/wowwiki.py
#
#

__copyright__ = 'this file is in the public domain'

from gozerbot.generic import geturl, striphtml, splittxt, handle_exception, \
fromenc
from gozerbot.commands import cmnds
from gozerbot.aliases import aliases
from gozerbot.examples import examples
from gozerbot.utils.rsslist import rsslist
from gozerbot.plughelp import plughelp
from urllib import quote
import re

plughelp.add('wowwiki', 'query wowwiki')

wikire = re.compile('start content(.*?)end content', re.M)

def getwikidata(url, ievent):
    """ fetch wiki data """
    try:
        result = fromenc(geturl(url))
    except IOError, ex:
        try:
            errno = ex[0]
        except IndexError:
            handle_exception(ievent=ievent)
            return
        ievent.reply('invalid option')
        return
    if not result:
        ievent.reply("can't find data for %s" % url)
        return
    res = rsslist(result)
    txt = ""
    for i in res:
        try:
            txt = i['text']
            break
        except:
            pass
    if not txt:
        ievent.reply("no data found on %s" % url)
        return
    #txt = re.sub('\[\[Image:([^\[\]]+|\[\[[^\]]+\]\])*\]\]', '', txt)
    txt = txt.replace('[[', '')
    txt = txt.replace(']]', '')
    txt = re.sub('\s+', ' ', txt)
    return txt

def handle_wowwiki(bot, ievent):
    """ wikipedia <what> .. search wikipedia for <what> """
    if not ievent.rest:
        ievent.missing('<what>')
        return
    what = ""
    lang = 'en'
    for i in ievent.rest.split():
        first = i[0].upper()
        rest = i[1:]
        if i.startswith('-'):
            if len(i) != 3:
                ievent.reply('invalid option')
                return
            lang = i[1:]
            continue
        what += "%s%s " % (first, rest)
    what = what.strip().replace(' ', '_')
    url = 'http://wowwiki.com/wiki/Special:Export/%s' % quote(what.encode('utf-8'))
    url2 = 'http://wowwiki.com/wiki/%s' % quote(what.encode('utf-8'))
    txt = getwikidata(url, ievent)
    if not txt:
        return
    if '#REDIRECT' in txt or '#redirect' in txt:
        redir = ' '.join(txt.split()[1:])
        url = 'http://wowwiki.com/wiki/Special:Export/%s' % quote(redir.encode('utf-8'))
        url2 = 'http://wowwiki.com/wiki/%s' % quote(redir.encode('utf-8'))
        txt = getwikidata(url, ievent)
    if not txt:
        return
    res = ['%s ===> ' % url2, ]
    res += splittxt(striphtml(txt).strip())
    ievent.reply(res)

cmnds.add('wowwiki', handle_wowwiki, 'USER')
examples.add('wowwiki', 'wowwiki <what> .. search wowwiki for <what>','1) wowwiki \
gozerbot')
aliases.data['wow'] = 'wowwiki'
