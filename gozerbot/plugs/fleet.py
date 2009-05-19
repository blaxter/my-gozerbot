# plugs/fleet.py
#
#

""" the fleet makes it possible to run multiple bots in one gozerbot.
    this can both be irc and jabber bots
"""

__copyright__ = 'this file is in the public domain'
__gendoclast__ = ['fleet-disconnect', 'fleet-del']

# gozerbot imports
from gozerbot.threads.thr import start_new_thread
from gozerbot.fleet import fleet
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
from gozerbot.aliases import aliasset
from gozerbot.config import config, Config, fleetbotconfigtxt
from gozerbot.datadir import datadir
from gozerbot.tests import tests

# basic imports
import os

plughelp.add('fleet', 'manage list of bots')

def handle_fleetavail(bot, ievent):

    """ show available fleet bots. """

    ievent.reply('available bots: ', fleet.avail()) 

cmnds.add('fleet-avail', handle_fleetavail, 'OPER')
examples.add('fleet-avail', 'show available fleet bots', 'fleet-avail')

def handle_fleetconnect(bot, ievent):

    """ fleet-connect <botname> .. connect a fleet bot to it's server. """

    try:
        botname = ievent.args[0]
    except IndexError:
        ievent.missing('<botname>')
        return

    try:
        if fleet.connect(botname):
            ievent.reply('%s connected' % botname)
        else:
            ievent.reply("can't connect %s" % botname)
    except Exception, ex:
        ievent.reply(str(ex))

cmnds.add('fleet-connect', handle_fleetconnect, 'OPER', threaded=True)
examples.add('fleet-connect', 'connect bot with <name> to irc server', 'fleet-connect test')
tests.add('fleet-add local test localhost').add('fleet-connect local').add('fleet-del local')

def handle_fleetdisconnect(bot, ievent):

    """ fleet-disconnect <botname> .. disconnect a fleet bot from server. """

    try:
        botname = ievent.args[0]
    except IndexError:
        ievent.missing('<botname>')
        return

    ievent.reply('exiting %s' % botname)

    try:
        if fleet.exit(botname):
            ievent.reply("%s bot stopped" % botname)
        else:
            ievent.reply("can't stop %s bot" % botname)
    except Exception, ex:
        ievent.reply(str(ex))

cmnds.add('fleet-disconnect', handle_fleetdisconnect, 'OPER', threaded=True)
examples.add('fleet-disconnect', 'fleet-disconnect <name> .. disconnect bot with <name> from irc server', 'fleet-disconnect test')
tests.add('fleet-add local test localhost').add('fleet-disconnect local').add('fleet-del local')

def handle_fleetlist(bot, ievent):

    """ fleet-list .. list bot names in fleet. """

    ievent.reply("fleet: ", fleet.list(), dot=True)

cmnds.add('fleet-list', handle_fleetlist, ['USER', 'WEB'])
examples.add('fleet-list', 'show current fleet list', 'fleet-list')
tests.add('fleet-add local test localhost').add('fleet-list local').add('fleet-del local')

def handle_fleetaddirc(bot, ievent):

    """ fleed-addirc <name> <nick> <server> [port] [passwd] [ipv6] .. add irc \
        bot to fleet.
    """

    from gozerbot.irc.bot import Bot
    length  = len(ievent.args)

    if length == 7:
        (name, nick, server, ipv6, ssl, port, password) = ievent.args
    elif length == 6:
        (name, nick, server, ipv6, ssl, port) = ievent.args
        password = ""
    elif length == 5:
        (name, nick, server, ipv6, ssl) = ievent.args
        password = ""
        if ssl:
           port = 6697
        else:
           port = 6667
    elif length == 4:
        (name, nick, server, ipv6) = ievent.args
        password = ""
        ssl = 0
        port = 6667
    elif length == 3:
        (name, nick, server) = ievent.args
        port = 6667
        password = ""
        ssl = 0
        ipv6 = 0
    else:
        ievent.missing('<name> <nick> <server> [<ipv6>] [<ssl>] [<port>] \
[<password>]')
        return

    if fleet.byname(name):
        ievent.reply('we already have a bot with %s name in fleet' % \
name)
        return

    if '--port' in ievent.optionset:
        port = ievent.options['--port']

    cfg = Config(datadir + os.sep + 'fleet' + os.sep + name, 'config', \
fleetbotconfigtxt)
    cfg['name'] = name
    cfg['nick'] = nick
    cfg['server'] = server
    cfg['port'] = port
    cfg['password'] = password
    cfg['ipv6'] = ipv6
    cfg['ssl'] = ssl
    cfg.save()
    b = fleet.makebot(name, cfg)

    try:
        ievent.reply('adding bot: %s' % str(b))
        fleet.addbot(b)
        ievent.reply('connecting to %s' % server)
        fleet.connect(name)
        ievent.reply('%s started' % name)
    except Exception, ex:
        ievent.reply(str(ex))
        fleet.delete(b)

cmnds.add('fleet-addirc', handle_fleetaddirc, 'OPER', options={'--port': '6667'}, threaded=True)
examples.add('fleet-addirc', 'fleet-addirc <name> <nick> <server> [ipv6] [port] [passwd] .. add new server to fleet', 'fleet-addirc test3 gozertest localhost')
aliasset('fleet-add', 'fleet-addirc')
tests.add('fleet-add local test localhost', 'started').add('fleet-del local')

def handle_fleetaddjabber(bot, ievent):

    """ fleed-addjabber <name> <host> <user> <password> [port] .. add jabber 
        bot to fleet.
    """
    try:
        import xmpp
    except ImportError:
        ievent.reply('xmpp is not enabled .. install the xmpppy package')
        return

    from gozerbot.jabber.jabberbot import Jabberbot

    if not bot.type == 'jabber':
        ievent.reply('use this command on a jabber bot (and change \
password if you used it)')
        return

    if ievent.groupchat:
        ievent.reply('use this command in a private message (and change \
password if you used it)')
        return

    length  = len(ievent.args)

    if length == 5:
        (name, host, user, password, port) = ievent.args
    elif length == 4:
        (name, host, user, password) = ievent.args
        port = 5222
    else:
        ievent.missing('<name> <host> <user> <password> [<port>]')
        return

    if fleet.byname(name):
        ievent.reply('we already have a bot with %s name in fleet' % \
name)
        return

    if '--port' in ievent.optionset:
        port = ievent.options['--port']

    cfg = Config(datadir + os.sep + 'fleet' + os.sep + name, 'config')
    cfg['name'] = name
    cfg['type'] = 'jabber'
    cfg['host'] = host
    cfg['user'] = user
    cfg['password'] = password
    cfg['port'] = port
    cfg.save()
    b = fleet.makebot(name, cfg)

    try:
        ievent.reply('added %s bot' % name)
        fleet.addbot(b)
        ievent.reply('connecting to %s' % server)
        fleet.connect(name)
        ievent.reply('%s started' % name)
    except Exception, ex:
        ievent.reply(str(ex))
        fleet.delete(b)

cmnds.add('fleet-addjabber', handle_fleetaddjabber, 'OPER', options={'--port': '5222'}, threaded=True)
examples.add('fleet-addjabber', 'fleet-addjabber <name> <host> <user> <passwd> [<port>] .. add new jabber server to fleet', 'fleet-addjabber test2 jabber.xs4all.nl jtest@jabber.xs4all.nl xwe23')

def handle_fleetdel(bot, ievent):

    """ fleet-del <botname> .. delete bot from fleet. """

    try:
        name = ievent.args[0]
    except IndexError:
        ievent.missing('<name>')
        return

    try:
        if fleet.delete(name):
            ievent.reply('%s deleted' % name)
        else:
            ievent.reply('%s delete failed' % name)
    except Exception, ex:
        ievent.reply(str(ex))

cmnds.add('fleet-del', handle_fleetdel, 'OPER', threaded=True)
examples.add('fleet-del', 'fleet-del <botname> .. delete bot from fleet list', 'fleet-del test')
tests.add('fleet-add local test localhost').add('fleet-del local', 'deleted')

def docmnd(bot, ievent):

    """ cmnd 'all'|<botname> <cmnd> .. do command on bot/all bots. """

    try:
        name = ievent.args[0]
        cmnd = ' '.join(ievent.args[1:])
    except IndexError:
        ievent.missing('<name> <cmnd>')
        return

    if not cmnd:
        ievent.missing('<name> <cmnd>')
        return

    if cmnd.find('cmnd') != -1:
        ievent.reply("no looping please ;]")
        return

    try:
        if name == 'all':
            fleet.cmndall(ievent, cmnd)
        else:
            fleet.cmnd(ievent, name, cmnd)
    except Exception, ex:
        ievent.reply(str(ex))

cmnds.add('cmnd', docmnd, ['USER', 'WEB'], threaded=True)
examples.add('cmnd', "cmnd all|<botname> <cmnd> .. excecute command on bot with <name> or on all fleet bots", '1) cmnd main st 2) cmnd all st')
tests.add('fleet-add local test localhost').add('cmnd --chan #dunkbots local nicks')

def fleet_disable(bot, ievent):

    """ disable a fleet bot. """

    if not ievent.rest:
        ievent.missing("list of fleet bots")
        return

    bots = ievent.rest.split()

    for name in bots:
        bot = fleet.byname(name)
        if bot:
            bot.cfg['enable'] = 0
            bot.cfg.save()
            ievent.reply('disabled %s' % name)
            fleet.exit(name)
        else:
            ievent.reply("can't find %s bot in fleet" % name)

cmnds.add('fleet-disable', fleet_disable, 'OPER')
examples.add('fleet-disable', 'disable a fleet bot', 'fleet-disable local')
tests.add('fleet-add local test localhost').add('fleet-disable local', 'disabled')

def fleet_enable(bot, ievent):

    """ enable a fleet bot. """

    if not ievent.rest:
        ievent.missing("list of fleet bots")
        return

    bots = ievent.rest.split()

    for name in bots:
        bot = fleet.byname(name)

        if bot:
            bot.cfg['enable'] = 1
            bot.cfg.save()
            ievent.reply('enabled %s' % name)
            start_new_thread(fleet.connect, (name, ))
        elif name in fleet.avail():
            bots = fleet.start([name, ], enable=True)
            for bot in bots:
                ievent.reply('enabled and started %s bot' % name)
                start_new_thread(fleet.connect, (name, ))
        else:
            ievent.reply('no %s bot in fleet' % name)

cmnds.add('fleet-enable', fleet_enable, 'OPER', threaded=True)
examples.add('fleet-enable', 'enable a fleet bot', 'fleet-enable local')
tests.add('fleet-add local test localhost').add('fleet-disable local').add('fleet-enable local')
