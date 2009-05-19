# plugs/url.py
#
#

from gozerbot.generic import handle_exception, rlog, convertpickle
from gozerbot.callbacks import callbacks
from gozerbot.commands import cmnds
from gozerbot.plughelp import plughelp
from gozerbot.examples import examples
from gozerbot.datadir import datadir
from gozerbot.persist.persiststate import PlugState
import re, os

plughelp.add('url', 'maintain searchable logs of urls')

def upgrade():
    convertpickle(datadir + os.sep + 'old' + os.sep + 'url', \
datadir + os.sep + 'plugs' + os.sep + 'url' + os.sep + 'state') 
    
re_url_match  = re.compile(u'((?:http|https)://\S+)')
state = None

def init():
    global state
    state = PlugState()
    state.define('urls', {})
    return 1

def shutdown():
    if len(state.data['urls']) > 0:
        state.save()
    return 1

def size():
    s = 0
    for i in state['urls'].values():
        for j in i.values():
            s += len(j)
    return s

def search(what, queue):
    rlog(10, 'url', 'searched for %s' % what)
    result = []
    try:
        for i in state['urls'].values():
            for urls in i.values():
                for url in urls:
                    if what in url:
                        result.append(url)
    except KeyError:
        pass
    for url in result:
        queue.put_nowait(url)

def urlpre(bot, ievent):
    return re_url_match.findall(ievent.txt)

def urlcb(bot, ievent):
    if not state:
        return 
    try:
        test_urls = re_url_match.findall(ievent.txt)
        for i in test_urls:
            if not state['urls'].has_key(bot.name):
                state['urls'][bot.name] = {}
            if not state['urls'][bot.name].has_key(ievent.channel):
                state['urls'][bot.name][ievent.channel] = []
            if not i in state['urls'][bot.name][ievent.channel]:
                state['urls'][bot.name][ievent.channel].append(i)  
    except Exception, ex:
        handle_exception()

callbacks.add('PRIVMSG', urlcb, urlpre, threaded=True)

def handle_urlsearch(bot, ievent):
    if not state:
        ievent.reply('rss state not initialized')
        return
    if not ievent.rest:
        ievent.missing('<what>')
        return
    result = []
    try:
        for i in state['urls'][bot.name][ievent.channel]:
            if ievent.rest in i:
                result.append(i)
    except KeyError:
        ievent.reply('no urls known for channel %s' % ievent.channel)
        return
    except Exception, ex:
        ievent.reply(str(ex))
        return
    if result:
        ievent.reply('results matching %s: ' % ievent.rest, result, nr=True)
    else:
        ievent.reply('no result found')
        return

cmnds.add('url-search', handle_urlsearch, ['USER', 'WEB', 'CLOUD'])
examples.add('url-search', 'search matching url entries', 'url-search gozerbot')

def handle_urlsearchall(bot, ievent):
    if not state:
        ievent.reply('rss state not initialized')
        return
    if not ievent.rest:
        ievent.missing('<what>')
        return
    result = []
    try:
        for i in state['urls'].values():
            for urls in i.values():
                for url in urls:
                    if ievent.rest in url:
                        result.append(url)
    except Exception, ex:
        ievent.reply(str(ex))
        return
    if result:
        ievent.reply('results matching %s: ' % ievent.rest, result, nr=True)
    else:
        ievent.reply('no result found')
        return

cmnds.add('url-searchall', handle_urlsearchall, ['USER', 'WEB', 'CLOUD'])
examples.add('url-searchall', 'search matching url entries', 'url-searchall \
gozerbot')

def handle_urlsize(bot, ievent):
    ievent.reply(str(size()))

cmnds.add('url-size', handle_urlsize, 'OPER')
examples.add('url-size', 'show number of urls in cache', 'url-size')
