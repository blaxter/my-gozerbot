# gozerplugs/plugs/supylog.py
#
#

""" log irc channels in supybot channellogger format """

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

plughelp.add('supylog', 'log irc channels in supybot channellogger format')

outlock = thread.allocate_lock()
outlocked = lockdec(outlock)

cfg = PersistConfig()
cfg.define('channels', [])
cfg.define('logtimestamp', '%Y-%m-%dT%H:%M:%S')
cfg.define('filenametimestamp', '%d-%a-%Y')
cfg.define('nologprefix', '[nolog]')
cfg.define('nologmsg', '-= THIS MESSAGE NOT LOGGED =-')

logfiles = {}
stopped = False

nonchanevents = ['NICK','NOTICE','QUIT']

if not os.path.isdir('logs'):
    os.mkdir('logs')
if not os.path.isdir('logs' + os.sep + 'supy'):
    os.mkdir('logs' + os.sep + 'supy')

for chan in cfg.get('channels'):
    if not os.path.isdir('logs' + os.sep + 'supy' + os.sep + chan[0]):
        os.mkdir('logs' + os.sep + 'supy' + os.sep + chan[0])
    if not os.path.isdir('logs' + os.sep + 'supy' + os.sep + chan[0] + os.sep + chan[1]):
        os.mkdir('logs' + os.sep + 'supy' + os.sep + chan[0] + os.sep + chan[1])

def init():
    global stopped
    callbacks.add('ALL', supylogcb, presupylogcb)
    jcallbacks.add('ALL', jabbersupylogcb, jabberpresupylogcb)
    outmonitor.add('supylog', supylogcb, presupylogcb)
    jabbermonitor.add('supylog', jabbersupylogcb, jabberpresupylogcb)
    stopped = False
    return 1

def shutdown():
    global stopped
    stopped = True
    for file in logfiles.values():
        file.close()
    return 1

def timestr():
    return time.strftime(cfg.get('logtimestamp'))

def write(bot, channel, txt):
    if stopped:
        return
    f = channel+ '.' + time.strftime(cfg.get('filenametimestamp')) + '.log'
    
    try:
        logfiles[f].write(txt)
        logfiles[f].flush()
    except (KeyError, IOError):
        if not os.path.isdir('logs' + os.sep + 'supy' + os.sep + bot.name + os.sep + channel):
            os.mkdir('logs' + os.sep + 'supy' + os.sep + bot.name + os.sep + channel)
        logfiles[f] = open('logs' + os.sep + 'supy' + os.sep + bot.name + os.sep + channel + os.sep + f, 'a')
        logfiles[f].write(txt)
        logfiles[f].flush()
    except Exception, ex:
        handle_exception()

def log(bot, ievent):
    chan = ievent.channel
    if ievent.cmnd == 'PRIVMSG':
        if ievent.txt.startswith('\001ACTION'):
            txt = ievent.txt[7:-1].strip()
            write(bot, chan, '%s  * %s %s\n' % (timestr(), ievent.nick, txt))
        elif ievent.txt.startswith(cfg.get('nologprefix')):
            write(bot, chan, '%s  <%s> %s\n' % (timestr(), ievent.nick, cfg.get('nologmsg')))
        else:
            write(bot, chan, '%s  <%s> %s\n' % (timestr(), ievent.nick, \
ievent.origtxt))
    elif ievent.cmnd == 'TOPIC':
        write(bot, chan, '%s  *** %s changes topic to "%s"\n' % (timestr(), ievent.nick, \
ievent.txt))
    elif ievent.cmnd == 'MODE':
        write(bot, chan, '%s  *** %s sets mode: %s\n' % (timestr(), ievent.nick, \
' '.join(ievent.arguments[1:])))
    elif ievent.cmnd == 'JOIN':
        write(bot, chan, '%s  *** %s has joined %s\n' % (timestr(), ievent.nick, \
chan))
    elif ievent.cmnd == 'KICK':
        write(bot, chan, '%s  *** %s was kicked by %s (%s)\n' % (timestr(), ievent.arguments[1], \
ievent.nick, ievent.txt, ))
    elif ievent.cmnd == 'PART':
        write(bot, chan, '%s  *** %s has left %s\n' % (timestr(), ievent.nick, \
chan))
    elif ievent.cmnd == 'QUIT':
        if not bot.userchannels.has_key(ievent.nick):
            return
        for c in bot.userchannels[ievent.nick]:
            if (bot.name, c) in cfg.get('channels') and c in bot.state['joinedchannels']:
                write(bot, c, '%s  *** %s has quit IRC\n' % (timestr(), ievent.nick))
    elif ievent.cmnd == 'NICK':
        if not bot.userchannels.has_key(ievent.nick):
            return
        for c in bot.userchannels[ievent.nick]:
            if (bot.name, c) in cfg.get('channels') and c in bot.state['joinedchannels']:
                write(bot, c, '%s  *** %s is now known as %s\n' % (timestr(), ievent.nick, \
ievent.txt))
    elif ievent.cmnd == 'NOTICE':
        if ievent.target[0] == '#':
            write(bot, ievent.target, '%s  -%s- %s\n' % (timestr(), ievent.nick, \
ievent.txt))

def jabberlog(bot, ievent):
    if ievent.botoutput:
        chan = ievent.to
    else:
        chan = ievent.channel
    if ievent.cmnd == 'Message':
            txt = ievent.txt.strip()
            write(bot, chan, '%s  <%s> %s\n' % (timestr(), ievent.nick, txt))
    elif ievent.cmnd == 'Presence':
            if ievent.type == 'unavailable':
               txt = "*** %s left" % ievent.nick
            else:
               txt = "*** %s joined" % ievent.nick
            write(bot, chan, '%s  %s\n' % (timestr(), txt))

def presupylogcb(bot, ievent):
    if not ievent.msg and (bot.name, ievent.channel) in cfg.get('channels') or \
ievent.cmnd in nonchanevents:
        return 1

def supylogcb(bot, ievent):
    log(bot, ievent)

def jabberpresupylogcb(bot, ievent):
    if not ievent.groupchat:
        return 0
    if (bot.name, ievent.channel) in cfg.get('channels') or ievent.botoutput:
        return 1

def jabbersupylogcb(bot, ievent):
    jabberlog(bot, ievent)

def handle_supylogon(bot, ievent):
    chan = ievent.channel
    if (bot.name, chan) not in cfg.get('channels'):
        cfg.get('channels').append((bot.name, chan))
        cfg.save()
        ievent.reply('supylog enabled on (%s,%s)' % (bot.name, chan))
    else:
        ievent.reply('supylog already enabled on (%s,%s)' % (bot.name, \
chan))
    if not os.path.isdir('logs' + os.sep + 'supy' + os.sep + bot.name):
        os.mkdir('logs' + os.sep + 'supy' + os.sep + bot.name)
    if not os.path.isdir('logs' + os.sep + 'supy' + os.sep + bot.name + os.sep + chan):
        os.mkdir('logs' + os.sep + 'supy' + os.sep + bot.name + os.sep + chan)

cmnds.add('supylog-on', handle_supylogon, 'OPER')
examples.add('supylog-on', 'enable supylog on <channel> or the channel \
the commands is given in', '1) supylog-on 2) supylog-on #dunkbots')

def handle_supylogoff(bot, ievent):
    try:
        cfg.get('channels').remove((bot.name, ievent.channel))
        cfg.save()
    except ValueError:
        ievent.reply('supylog is not enabled in (%s,%s)' % (bot.name, \
ievent.channel))
        return
    ievent.reply('supylog disabled on (%s,%s)' % (bot.name, ievent.channel))

cmnds.add('supylog-off', handle_supylogoff, 'OPER')
examples.add('supylog-off', 'disable supylog on <channel> or the channel \
the commands is given in', '1) supylog-off 2) supylog-off #dunkbots')
