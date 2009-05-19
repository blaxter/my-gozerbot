# gozerplugs/plugs/simplelog.py
#
#

""" log irc channels to [hour:min] <nick> txt format """

__copyright__ = 'this file is in the public domain'

from gozerbot.commands import cmnds
from gozerbot.callbacks import callbacks, jcallbacks
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.generic import hourmin, rlog, lockdec
from gozerbot.monitor import outmonitor, jabbermonitor
from gozerbot.plughelp import plughelp
from gozerbot.examples import examples
from gozerbot.irc.ircevent import Ircevent
from gozerbot.fleet import fleet
import time, os, thread

plughelp.add('simplelog', 'log irc channels to [hour:min] <nick> txt format')

outlock = thread.allocate_lock()
outlocked = lockdec(outlock)

cfg = PersistConfig()
cfg.define('channels', [])

logfiles = {}
stopped = False

if not os.path.isdir('logs'):
    os.mkdir('logs')
if not os.path.isdir('logs' + os.sep + 'simple'):
    os.mkdir('logs' + os.sep + 'simple')


def init():
    global stopped
    callbacks.add('ALL', simplelogcb, presimplelogcb)
    jcallbacks.add('ALL', jabbersimplelogcb, jabberpresimplelogcb)
    outmonitor.add('simplelog', simplelogcb, presimplelogcb)
    jabbermonitor.add('simplelog', jabbersimplelogcb, jabberpresimplelogcb)
    stopped = False
    return 1

def shutdown():
    global stopped
    stopped = True
    for file in logfiles.values():
        file.close()
    return 1

def timestr():
    return time.strftime("%Y-%m-%d %H:%M:%S")

def write(channel, txt):
    if stopped:
        return
    f = channel+ '.' + time.strftime("%Y%m%d") + '.slog'
    try:
        logfiles[f].write(txt)
        logfiles[f].flush()
    except KeyError:
        try:
            logfiles[f] = open('logs/simple/' + f, 'a')
            logfiles[f].write(txt)
            logfiles[f].flush()
        except Exception, ex:
            rlog(10, 'simplelog', str(ex))
    except Exception, ex:
        rlog(10, 'simplelog', str(ex))

def log(bot, ievent):
    chan = ievent.channel
    if ievent.cmnd == 'PRIVMSG':
        if ievent.txt.startswith('\001ACTION'):
            txt = ievent.txt[7:-1].strip()
            write(chan, '%s | * %s %s\n' % (timestr(), ievent.nick, txt))
        else:
            write(chan, '%s | <%s> %s\n' % (timestr(), ievent.nick, \
ievent.origtxt))
    elif ievent.cmnd == 'MODE':
        write(chan, '%s | %s sets mode: %s\n' % (timestr(), ievent.nick, \
' '.join(ievent.arguments[1:])))
    elif ievent.cmnd == 'JOIN':
        write(chan[1:], '%s | %s (%s) has joined\n' % (timestr(), ievent.nick, \
ievent.userhost))
    elif ievent.cmnd == 'PART':
        write(chan[1:], '%s | %s (%s) has left\n' % (timestr(), ievent.nick, \
ievent.userhost))
    elif ievent.cmnd == 'QUIT':
        if not bot.userchannels.has_key(ievent.nick.lower()):
            return
        for c in bot.userchannels[ievent.nick.lower()]:
            if c in cfg.get('channels') and c in bot.state['joinedchannels']:
                write(c, '%s | %s (%s) has \
quit: %s\n' % (timestr(), ievent.nick, ievent.userhost, ievent.txt))

def jabberlog(bot, ievent):
    if ievent.botoutput:
        chan = ievent.to
    else:
        chan = ievent.channel
    if ievent.cmnd == 'Message':
            txt = ievent.txt.strip()
            write(chan, '%s | <%s> %s\n' % (timestr(), ievent.nick, txt))
    elif ievent.cmnd == 'Presence':
            if ievent.type == 'unavailable':
               txt = "%s left" % ievent.nick
            else:
               txt = "%s joined" % ievent.nick
            write(chan, '%s | %s\n' % (timestr(), txt))

def presimplelogcb(bot, ievent):
    if not ievent.msg and (bot.name, ievent.channel) in cfg.get('channels') or\
 ievent.cmnd == 'QUIT':
        return 1

def simplelogcb(bot, ievent):
    log(bot, ievent)

def jabberpresimplelogcb(bot, ievent):
    if not ievent.groupchat:
        return 0
    if (bot.name, ievent.channel) in cfg.get('channels') or ievent.botoutput:
        return 1

def jabbersimplelogcb(bot, ievent):
    jabberlog(bot, ievent)

def handle_simplelogon(bot, ievent):
    chan = ievent.channel
    if (bot.name, chan) not in cfg.get('channels'):
        cfg.get('channels').append((bot.name, chan))
        cfg.save()
        ievent.reply('simplelog enabled on (%s,%s)' % (bot.name, chan))
    else:
        ievent.reply('simplelog already enabled on (%s,%s)' % (bot.name, \
chan))
cmnds.add('simplelog-on', handle_simplelogon, 'OPER')
examples.add('simplelog-on', 'enable simplelog on <channel> or the channel \
the commands is given in', '1) simplelog-on 2) simplelog-on #dunkbots')

def handle_simplelogoff(bot, ievent):
    try:
        cfg.get('channels').remove((bot.name, ievent.channel))
        cfg.save()
    except ValueError:
        ievent.reply('simplelog is not enabled in (%s,%s)' % (bot.name, \
ievent.channel))
        return
    ievent.reply('simplelog disabled on (%s,%s)' % (bot.name, ievent.channel))

cmnds.add('simplelog-off', handle_simplelogoff, 'OPER')
examples.add('simplelog-off', 'disable simplelog on <channel> or the channel \
the commands is given in', '1) simplelog-off 2) simplelog-off #dunkbots')
