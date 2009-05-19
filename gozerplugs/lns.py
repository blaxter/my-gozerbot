# http://ln-s.net short ln-s
# (c) Wijnand "tehmaze" Modderman - http://tehmaze.com
# BSD License

from gozerbot.aliases import aliases
from gozerbot.callbacks import callbacks
from gozerbot.commands import cmnds
from gozerbot.generic import rlog
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.persist.persiststate import PlugState
from gozerbot.plughelp import plughelp
from gozerbot.examples import examples
import re
import urllib, urllib2

plughelp.add('lns', 'use the ln-s.net redirector')

re_url_match = re.compile(r'((?:http|https|ftp)://\S+)')

cfg = PersistConfig()
cfg.define('url-api', 'http://ln-s.net/home/api.jsp')
cfg.define('url-len', 64)

state = None

def init():
    global state
    state = PlugState()
    state.define('ln-s', {})
    return 1

def shutdown():
    state.save()
    return 1

def lnsurl(url):
    req = urllib2.Request(url=cfg.get('url-api'),
        data=urllib.urlencode({'url': url}))
    out = urllib2.urlopen(req)
    ret = out.read().strip()
    return ret.split(' ', 1)[1]

def lnscb(bot, ievent):
    if not state:
        return
    if not bot.name in state['ln-s']:
        return
    if not ievent.channel.lower() in state['ln-s'][bot.name]:
        return
    if not state['ln-s'][bot.name][ievent.channel.lower()]:
        return
    try:
        test_urls = re_url_match.findall(ievent.txt)
        for url in test_urls:
            if len(url) >= cfg.get('url-len'):
                host = url.split(':')[1].lstrip('/').split('/')[0]
                short = lnsurl(url)
                ievent.reply('%s (at %s)' % (short, host))
    except Exception,e:
        rlog(10, 'lns', 'EXCEPTION: %s' % str(e))

def handle_ln_on(bot, ievent):
    if not bot.name in state['ln-s']:
        state['ln-s'][bot.name] = {}
    if not ievent.channel.lower() in state['ln-s'][bot.name]:
        state['ln-s'][bot.name][ievent.channel.lower()] = True
    ievent.reply('ok')

def handle_ln_off(bot, ievent):
    if not bot.name in state['ln-s']:
        state['ln-s'][bot.name] = {}
    if not ievent.channel.lower() in state['ln-s'][bot.name]:
        state['ln-s'][bot.name][ievent.channel.lower()] = False
    ievent.reply('ok')

callbacks.add('PRIVMSG', lnscb)
cmnds.add('ln-on', handle_ln_on, 'USER')
examples.add('ln-on', 'enable ln in channel the command was given in', 'ln-on')
cmnds.add('ln-off', handle_ln_off, 'USER')
examples.add('ln-off', 'diable ln in channel the command was given in', \
'ln-off')
aliases.data['lns-on'] = 'ln-on'
aliases.data['lns-off'] = 'lns-off'
