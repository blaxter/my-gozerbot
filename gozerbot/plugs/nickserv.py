# gozerbot/plugs/nickserv.py
#
# let gozerbot authenticate to NickServ


""" authenticate to NickServ. """

__author__ = "Wijnand 'tehmaze' Modderman - http://tehmaze.com"
__license__ ='BSD'
__gendoclast__ = ['ns-del', ]

# gozerbot imports
from gozerbot.utils.generic import convertpickle
from gozerbot.examples import examples
from gozerbot.callbacks import callbacks
from gozerbot.commands import cmnds
from gozerbot.datadir import datadir
from gozerbot.fleet import fleet
from gozerbot.persist.pdod import Pdod
from gozerbot.plughelp import plughelp
from gozerbot.generic import rlog
from gozerbot.config import config
from gozerbot.tests import tests

# basic imports
import os, time

plughelp.add('nickserv', 'authenticate the bot through (nick)services')

## UPGRADE PART

def upgrade():

    """ upgrade the nickserv data. """

    try:
        convertpickle(datadir + os.sep + 'nickserv', datadir + os.sep + 'plugs' + os.sep + \
'nickserv' + os.sep + 'nickserv')
    except Exception, ex:
        rlog(10, 'nickserv', 'failed to upgrade .. %s' % str(ex))

## END UPGRADE PART

class NSAuth(Pdod):

    """ nickserve auth. """

    def __init__(self):
        self.registered = False
        Pdod.__init__(self, datadir + os.sep + 'plugs' + os.sep + \
'nickserv' + os.sep + 'nickserv')

    def add(self, bot, **kwargs):

        """ add a nickserv entry. """

        options = {
            'nickserv': 'NickServ',
            'identify': 'IDENTIFY',
        }

        options.update(kwargs)
        assert options.has_key('password'), 'A password must be set'

        for key in options.keys():
            Pdod.set(self, bot.name, key, options[key])

        self.save()

    def remove(self, bot):

        """ remove a nickserv entry. """

        if self.has_key(bot.name):
            del self[bot.name]
            self.save()

    def has(self, bot):

        """ check if a bot is in the nickserv list. """

        return self.has_key(bot.name)

    def register(self, bot, passwd):

        """ register a bot to nickserv. """

        if self.has_key(bot.name) and self.has_key2(bot.name, 'nickserv'):
            bot.sendraw('PRIVMSG %s :%s %s' % (self.get(bot.name, \
'nickserv'),  'REGISTER', passwd))
            rlog(10, 'nickserv', 'register sent on %s' % bot.server)

    def identify(self, bot):

        """ identify a bot to nickserv. """

        if self.has_key(bot.name) and self.has_key2(bot.name, 'nickserv'):
            bot.say(self.get(bot.name, 'nickserv', ), '%s %s' % (self.get(bot.name, 'identify'), self.get(bot.name, 'password')), speed=9)
            rlog(10, 'nickserv', 'identify sent on %s' % bot.server)

    def listbots(self):

        """ list all bots know. """
 
        all = []

        for bot in self.data.keys():
            all.append((bot, self.data[bot]['nickserv']))

        return all

    def sendstring(self, bot, txt):

        """ send string to nickserver. """

        nickservnick = self.get(bot.name, 'nickserv')
        bot.say(nickservnick, txt)

    def handle_001(self, bot, ievent):
        self.identify(bot)
        try:
            for i in self.data[bot.name]['nickservtxt']:
                self.sendstring(bot, i)
                rlog(10, 'nickserv', 'sent %s' % i)
        except:
            pass

# basic init stuff
nsauth = NSAuth()

if not nsauth.data:
    upgrade()
    nsauth = NSAuth()

callbacks.add('001', nsauth.handle_001, threaded=True)

def init():

    """ init the nickserv data. """

    passwd = config['nickservpass']
    if passwd:
        nsauth.add(bot, **{'password': passwd, 'nickservtxt': config['nickservtxt']})
    return 1

def handle_nsadd(bot, ievent):

    """ add a bot to the nickserv. """

    if bot.jabber:
        return

    if len(ievent.args) < 1:
        ievent.missing('<password> [<nickserv nick>] [<identify command>]')
        return

    if nsauth.has(bot):
        ievent.reply('replacing previous configuration')

    options = {}

    if len(ievent.args) >= 1:
        options.update({'password': ievent.args[0]})

    if len(ievent.args) >= 2:
        options.update({'nickserv': ievent.args[1]})

    if len(ievent.args) >= 3:
        options.update({'identify': ' '.join(ievent.args[2:])})

    nsauth.add(bot, **options)
    ievent.reply('ok')

cmnds.add('ns-add', handle_nsadd, 'OPER', threaded=True)
examples.add('ns-add', 'ns-add <password> [<nickserv nick>] [<identify command>] .. add nickserv', 'ns-add mekker')
tests.add('ns-add mekker', 'ok')

def handle_nsdel(bot, ievent):

    """ remove a bot from nickserv. """

    if bot.jabber:
        return

    if len(ievent.args) != 1:
        ievent.missing('<fleetbot name>')
        return

    fbot = fleet.byname(ievent.args[0])

    if not fbot:
        ievent.reply('fleet not found')
        return

    if not nsauth.has(fbot):
        ievent.reply('nickserv not configured on %s' % fbot.name)
        return
    nsauth.remove(fbot)
    ievent.reply('ok')

cmnds.add('ns-del', handle_nsdel, 'OPER', threaded=True)
examples.add('ns-del', 'ns-del <fleetbot name>', 'ns-del test')
tests.add('ns-del default', 'ok')

def handle_nssend(bot, ievent):

    """ send string to the nickserv. """

    if bot.jabber:
        return

    if not ievent.rest:
        ievent.missing('<txt>')
        return

    nsauth.sendstring(bot, ievent.rest)    
    ievent.reply('send')

cmnds.add('ns-send', handle_nssend, 'OPER', threaded=True)
examples.add('ns-send', 'ns-send <txt> .. send txt to nickserv', 'ns-send identify bla')
#tests.add('ns_send', 'send')

def handle_nsauth(bot, ievent):

    """ perform an auth request. """

    if bot.jabber:
        return

    if len(ievent.args) != 1:
        name = bot.name
    else:
        name = ievent.args[0]

    fbot = fleet.byname(name)

    if not fbot:
        ievent.reply('fleet not found')
        return

    if not nsauth.has(fbot):
        ievent.reply('nickserv not configured on %s' % fbot.name)
        return

    nsauth.identify(fbot)
    ievent.reply('ok')

cmnds.add('ns-auth', handle_nsauth, 'OPER', threaded=True)
examples.add('ns-auth','ns-auth [<botname>]', '1) ns-auth 2) ns-auth test')
tests.add('ns-add mekker').add('ns-auth default', 'ok')

def handle_nslist(bot, ievent):

    """ show a list of all bots know with nickserv. """

    if bot.jabber:
        return

    all = dict(nsauth.listbots())
    rpl = []

    for bot in all.keys():
        rpl.append('%s: authenticating through %s' % (bot, all[bot]))

    rpl.sort()
    ievent.reply(' .. '.join(rpl))

cmnds.add('ns-list', handle_nslist, 'OPER')
examples.add('ns-list', 'list all nickserv entries', 'ns-list')
tests.add('ns-list')
