# rudimentary authentication trough nickserv
# Wijnand 'tehmaze' Modderman - http://tehmaze.com
# BSD License

from gozerbot.utils.generic import convertpickle
from gozerbot.callbacks import callbacks
from gozerbot.commands import cmnds
from gozerbot.datadir import datadir
from gozerbot.fleet import fleet
from gozerbot.users import users
from gozerbot.persist.pdod import Pdod
from gozerbot.plughelp import plughelp
import os

plughelp.add('identify', 'auto-merges identified users')

##3 UPGRADE PART

def upgrade():
    convertpickle(datadir + os.sep + 'old' + os.sep + 'identify', \
datadir + os.sep + 'plugs' + os.sep + 'identify' + os.sep + 'identify')

## END UPGRADE PART

class IdManager(Pdod):
    def __init__(self):
        Pdod.__init__(self, os.path.join(datadir, 'identify'))
        self.setup()

    def setup(self):
        for bot in fleet.bots:
            self.check(bot)

    def check(self, bot):
        if not self.data.has_key(bot.name):
            self.data[bot.name] = {}

    def add(self, bot, nick, user):
        self.check(bot)
        self.data[bot.name][nick] = user
        self.save()

    def get(self, bot, nick):
        if not self.data.has_key(bot.name):
            return None
        if not self.data[bot.name].has_key(nick):
            return None
        return self.data[bot.name][nick]

    def lookup(self, bot, nick, userhost):
        user = self.get(bot, nick)
        if user:
            users.adduserhost(user, userhost)
            return True
        return False

    def remove(self, bot, nick):
        if not self.data.has_key(bot.name):
            return False
        if not self.data[bot.name].has_key(nick):
            return False
        del self.data[bot.name][nick]
        self.save()
        return True

idmanager = IdManager()
if not idmanager.data:
    idmanager = IdManager()

def handle_id(bot, ievent):
    if not ievent.args:
        ievent.missing('<nick>')
        return
    ievent.reply('requesting userinfo for %s' % ievent.args[0])
    bot.sendraw('WHOIS %s' % ievent.args[0])

cmnds.add('id', handle_id, ['OPER'])

def handle_idadd(bot, ievent):
    if len(ievent.args) != 2:
        ievent.missing('<nick> <user>')
        return
    if idmanager.get(bot, ievent.args[0].lower()):
        ievent.reply('%s is already known on %s' % (ievent.args[0].lower(), bot.name))
        return
    if not users.exist(ievent.args[1]):
        ievent.reply('user %s unknown' % ievent.args[1].lower())
        return
    else:
        idmanager.add(bot, ievent.args[0].lower(), ievent.args[1].lower())
        ievent.reply('ok')
   
cmnds.add('id-add', handle_idadd, 'OPER')

def handle_idlist(bot, ievent):
    ievent.reply(str(idmanager.data))

cmnds.add('id-list', handle_idlist, 'OPER')

def handle_JOIN(bot, ievent):
    user = users.getname(ievent.userhost)
    if not user:
        user = idmanager.lookup(bot, ievent.nick.lower(), ievent.userhost)
    if not user:
        bot.sendraw('WHOIS %s' % ievent.nick)

callbacks.add('JOIN', handle_JOIN)

def handle_320_330(bot, ievent):
    text = ' '.join(ievent.arguments[2:])
    #bot.sendraw('PRIVMSG #dunkbots :%s' % str(ievent))
    # IRC protocol sucks, no generic code for identified users :-(
    # so,
    if ievent.cmnd == '320' and 'is identified to services' in text:
        # Freenode
        nick = ievent.arguments[1].lower()
        userhost = bot.userhosts[nick]
        idmanager.lookup(bot, nick, userhost) 
        #bot.sendraw('PRIVMSG #dunkbots :%s is identified (320/freenode)' % nick)
    elif ievent.cmnd == '330' and 'is logged in as' in text:
        # Undernet
        nick = ievent.arguments[1].lower()
        userhost = bot.userhosts[nick]
        idmanager.lookup(bot, nick, userhost)
        #bot.sendraw('PRIVMSG #dunkbots :%s is identified (330/undernet)' % nick)

callbacks.add('320', handle_320_330)
callbacks.add('330', handle_320_330)

