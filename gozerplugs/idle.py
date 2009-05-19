# plugs/idle.py
#
#

__copyright__ = 'this file is in the public domain'

from gozerbot.generic import elapsedstring, getwho, jsonstring
from gozerbot.commands import cmnds
from gozerbot.callbacks import callbacks, jcallbacks
from gozerbot.examples import examples
from gozerbot.datadir import datadir
from gozerbot.persist.persist import PlugPersist
from gozerbot.plughelp import plughelp
from gozerbot.aliases import aliases
import time, os

plughelp.add('idle', 'show how long a user or channel has been idle')

idle = PlugPersist('idle.data')
if not idle.data:
    idle.data = {}

def shutdown():
    idle.save()

def preidle(bot, ievent):
    """ idle precondition aka check if it is not a command """
    if ievent.usercmnd:
        return 0
    else:
        return 1
        
def idlecb(bot, ievent):
    """ idle PRIVMSG callback .. set time for channel and nick """
    ttime = time.time()
    idle.data[jsonstring((bot.name, ievent.channel))] = ttime
    idle.data[jsonstring((bot.name, ievent.userhost))] = ttime

callbacks.add('PRIVMSG', idlecb, preidle)
jcallbacks.add('Message', idlecb, preidle)

def handle_idle(bot, ievent):
    """ idle [<nick>] .. show how idle an channel/user has been """
    try:
        who = ievent.args[0]
    except IndexError:
        handle_idle2(bot, ievent)
        return
    userhost = getwho(bot, who)
    if not userhost:
        ievent.reply("can't get userhost of %s" % who)
        return
    try:
        elapsed = elapsedstring(time.time() - idle.data[jsonstring((bot.name, userhost))])
    except KeyError:
        ievent.reply("i haven't seen %s" % who)
        return
    if elapsed:
        ievent.reply("%s is idle for %s" % (who, elapsed))
        return
    else:
        ievent.reply("%s is not idle" % who)
        return   

cmnds.add('idle', handle_idle, ['USER', 'WEB', 'CLOUD'])
aliases.data['st'] = 'idle'

def handle_idle2(bot, ievent):
    """ show how idle a channel has been """
    chan = ievent.channel
    try:
        elapsed = elapsedstring(time.time()-idle.data[jsonstring((bot.name, chan))])
    except KeyError:
        ievent.reply("nobody said anything on channel %s yet" % chan)
        return
    if elapsed:
        ievent.reply("channel %s is idle for %s" % (chan, elapsed))
    else:
        ievent.reply("channel %s is not idle" % chan)

examples.add('idle', 'idle [<nick>] .. show how idle the channel is or show \
how idle <nick> is', '1) idle 2) idle test')
