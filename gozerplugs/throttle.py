# gozerplugs/plugs/throttle.py
#
#

__depending__ = ['anon', ]

from gozerbot.persist.persiststate import PlugState
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.callbacks import callbacks
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
from gozerbot.users import users
from gozerbot.generic import getwho, rlog
import time

plughelp.add('throttle', 'throttle user commands per minute')

state = PlugState()
state.define('lasttime', {})
state.define('level', {})
state.define('cpm', {}) # commands per minute

cfg = PersistConfig()
cfg.define('enable', 1)

def throttlepre(bot, ievent):
    if cfg.get('enable'):
        return 1

def throttlecb(bot, ievent):
    try:
        cpm = state['cpm']
        uh = ievent.userhost
        if ievent.usercmnd:
            if cpm.has_key(uh):
                cpm[uh] += 1
            else:
                cpm[uh] = 1
        if uh in bot.throttle:
            if time.time() - state['lasttime'][uh] > 60:
                bot.throttle.remove(uh)
                cpm[uh] = 0
                ievent.reply('%s un-throttled' % uh)
                rlog(10, 'throttle', 'unignoring %s' % uh)
        else:
            if ievent.usercmnd and (cpm[uh] > state['level'][uh]):
                bot.throttle.append(uh)
                ievent.reply('%s throttled' % uh)
                rlog(10, 'throttle', 'ignoring %s' % uh)
                state['lasttime'][uh] = time.time()
    except (ValueError, KeyError):
        pass

def init():
    callbacks.add('PRIVMSG', throttlecb, throttlepre)

def handle_throttleget(bot, ievent):
    if not ievent.rest:
        ievent.missing("<nick>")
        return
    nick = ievent.rest
    uh = getwho(bot, nick)
    if not uh:
        ievent.reply("can't find userhost of %s" % nick)
        return
    try:
        ievent.reply("cpm of %s is %s" % (uh, state['level'][uh]))
    except KeyError:
        pass

cmnds.add('throttle-get', handle_throttleget, 'OPER')
examples.add('throttle-get', 'get commands per minute of <nick>', \
'throttle-get dunker')

def handle_throttleset(bot, ievent):
    try:
        (nick, cpm) = ievent.args
    except ValueError:
        ievent.missing('<nick> <commands per minute>')
        return
    uh = getwho(bot, nick)
    if not uh:
        ievent.reply("can't find userhost of %s" % nick)
        return
    perms = users.getperms(uh)
    if 'OPER' in perms:
        ievent.reply("can't throttle a OPER")
        return
    try:
        cpm = float(cpm)
        if cpm == 0:
            ievent.reply("cpm can't be zero")
            return
        state['level'][uh] = cpm
        state['cpm'][uh] = 0
        state.save()
    except ValueError:
        ievent.reply('%s is not an integer' % cpm)
        return
    try:
        bot.throttle.remove(uh)
    except ValueError:
        pass
    ievent.reply('cpm set to %s for %s' % (cpm, uh))
 
cmnds.add('throttle-set', handle_throttleset, 'OPER')
examples.add('throttle-set', 'set allowed <cpm> commands per minute for \
<nick>' , 'throttle-set dunker 10')

def handle_throttleremove(bot, ievent):
    if not ievent.rest:
        ievent.missing('<nick>')
        return
    uh = getwho(bot, ievent.rest)
    if not uh:
        ievent.reply("can't find userhost of %s" % ievent.rest)
        return
    try:
        bot.throttle.remove(uh)
        state['cpm'][uh] = 0
        state.save()
        ievent.reply('throttle on %s removed' % uh)
    except (KeyError, ValueError):
        pass

cmnds.add('throttle-remove', handle_throttleremove, 'OPER')
examples.add('throttle-remove', 'remove throttle from <nick>', \
'throttle-remove dunker')

def handle_throttlelist(bot, ievent):
    ievent.reply(bot.throttle)

cmnds.add('throttle-list', handle_throttlelist, 'OPER')
