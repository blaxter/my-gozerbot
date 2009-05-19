# gozerplugs/traclog.py
#
#

""" log irc channels in trac format (0.10.4) """

__copyright__ = 'this file is in the public domain'

from gozerbot.commands import cmnds
from gozerbot.callbacks import callbacks
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.generic import hourmin, rlog
from gozerbot.monitor import outmonitor
from gozerbot.plughelp import plughelp
from gozerbot.examples import examples
from gozerbot.irc.ircevent import Ircevent
from gozerbot.fleet import fleet
import time, os

plughelp.add('traclog', 'log irc channels in trac format')

cfg = PersistConfig()
cfg.define('channels', [])
cfg.define('tracversion', "0.11")

logfiles = {}

if not os.path.exists('logs/'):
    os.mkdir('logs/')
if not os.path.exists('logs/trac/'):
    os.mkdir('logs/trac/')

def init():
    callbacks.add('ALL', traclogcb, pretraclogcb)
    outmonitor.add('traclog', traclogcb, pretraclogcb)
    return 1

def shutdown():
    for file in logfiles.values():
        file.close()
    return 1

def timestr():
    if cfg.get('tracversion') == '0.10':
        return time.strftime("%Y-%m-%d %H:%M:%S |")
    else:
        return time.strftime("%Y-%m-%dT%H:%M:%S ")

def write(channel, txt):
    f = channel + '.' + time.strftime("%Y%m%d") + '.log'
    try:
        logfiles[f].write(txt)
        logfiles[f].flush()
    except KeyError:
        try:
            logfiles[f] = open('logs/trac/' + f, 'a')
            logfiles[f].write(txt)
            logfiles[f].flush()
        except Exception, ex:
            rlog(10, 'traclog', str(ex))
    except Exception, ex:
        rlog(10, 'traclog', str(ex))

def log(bot, ievent):
    chan = ievent.channel
    if ievent.cmnd == 'PRIVMSG':
        if ievent.txt.startswith('\001ACTION'):
            txt = ievent.txt[7:-1].strip()
            write(chan, '%s  * %s %s\n' % (timestr(), ievent.nick, txt))
        else:
            write(chan, '%s  <%s> %s\n' % (timestr(), ievent.nick, \
ievent.origtxt))
    elif ievent.cmnd == 'MODE':
        write(chan, '%s  %s sets mode: %s\n' % (timestr(), ievent.nick, \
' '.join(ievent.arguments[1:])))
    elif ievent.cmnd == 'JOIN':
        write(chan, '%s  %s (%s) has joined\n' % (timestr(), ievent.nick, \
ievent.userhost))
    elif ievent.cmnd == 'PART':
        write(chan, '%s  %s (%s) has left\n' % (timestr(), ievent.nick, \
ievent.userhost))
    elif ievent.cmnd == 'QUIT':
        if not bot.userchannels.has_key(ievent.nick):
            return
        for c in bot.userchannels[ievent.nick]:
            if c in cfg.get('channels') and c in bot.state['joinedchannels']:
                write(c, '%s  %s (%s) has \
quit: %s\n' % (timestr(), ievent.nick, ievent.userhost, ievent.txt))

def pretraclogcb(bot, ievent):
    if not ievent.msg and [bot.name, ievent.channel] in cfg.get('channels') or\
 ievent.cmnd == 'QUIT':
        return 1

def traclogcb(bot, ievent):
    log(bot, ievent)

def handle_traclogon(bot, ievent):
    if bot.jabber:
        ievent.reply("traclog only works on IRC")
        return
    chan = ievent.channel
    if [bot.name, chan] not in cfg.get('channels'):
        cfg.get('channels').append([bot.name, chan])
        cfg.save()
        ievent.reply('traclog enabled on (%s,%s)' % (bot.name, chan))
    else:
        ievent.reply('traclog already enabled on (%s,%s)' % (bot.name, \
chan))
cmnds.add('traclog-on', handle_traclogon, 'OPER')
examples.add('traclog-on', 'enable  traclog on <channel> or the channel \
the commands is given in', '1) traclog-on 2) traclog-on #dunkbots')

def handle_traclogoff(bot, ievent):
    try:
        cfg.get('channels').remove([bot.name, ievent.channel])
        cfg.save()
    except ValueError:
        ievent.reply('traclog is not enabled in (%s,%s)' % (bot.name, \
ievent.channel))
        return
    ievent.reply('traclog disabled on (%s,%s)' % (bot.name, ievent.channel))

cmnds.add('traclog-off', handle_traclogoff, 'OPER')
examples.add('traclog-off', 'disable traclog on <channel> or the channel \
the commands is given in', '1) traclog-off 2) traclog-off #dunkbots')
