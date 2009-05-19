# plugs/away.py
#
# 

""" keep away messages """

__copyright__ = 'this file is in the public domain'

from gozerbot.generic import rlog
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.callbacks import callbacks
from gozerbot.users import users
from gozerbot.plugins import plugins
from gozerbot.datadir import datadir
from gozerbot.persist.persist import PlugPersist
from gozerbot.plughelp import plughelp
from gozerbot.tests import tests
import time, os

plughelp.add('away', "keep notice of who's away")

lasttime = []

# use datadir/away as pickle file
awaydict = PlugPersist('away.data')

# see if data attribute is set otherwise init it
if not awaydict.data:
    awaydict.data = {}
if not awaydict.data.has_key('enable'):
    awaydict.data['enable'] = 0
    awaydict.save()

def init():
    """ init plugin """
    if not awaydict.data['enable']:
        rlog(0, 'away', 'away is disabled')
        return 1
    else:
        rlog(0, 'away', 'away is enabled')
    callbacks.add('PRIVMSG', doaway, awaytest)
    callbacks.add('PRIVMSG', doback, backtest)
    return 1

def awaytest(bot, ievent):
    """ test if away callback should be called """
    if (len(ievent.txt) > 1 and ievent.txt[-1] == '\001' and \
ievent.txt[-2] == '&' ) or ievent.txt.strip() == '&':
        return 1
        
def doaway(bot, ievent):
    """ away callback """
    if not users.allowed(ievent.userhost, 'USER'):
        return
    # use username of user giving the command
    name = users.getname(ievent.userhost)
    if not name:
        return
    if awaydict.data.has_key((name, bot.name, ievent.channel)):
        return
    ievent.reply("ltrs %s" % ievent.nick)
    # add away data to entry indexed by username, botname and channel
    awaydict.data[(name, bot.name, ievent.channel)] = time.time()
    awaydict.save()

def backtest(bot, ievent):
    """ test if we should say hello """
    if 'back' == ievent.txt.strip() or 're' == ievent.txt.strip():
        return 1
    
def doback(bot, ievent):
    """ say hello """
    if not users.allowed(ievent.userhost, 'USER'):
        return
    # reset away entry 
    name = users.getname(ievent.userhost)
    if not name:
        return
    if not awaydict.data.has_key((name, bot.name, ievent.channel)):
        return
    ievent.reply("welcome back %s" % ievent.nick)
    try:
        del awaydict.data[(name, bot.name, ievent.channel)]
        awaydict.save()
    except KeyError:
        pass

def handle_awayenable(bot, ievent):
    """ away-enable .. enable away """
    awaydict.data['enable'] = 1
    awaydict.save()
    plugins.reload('gozerplugs', 'away')
    ievent.reply('away enabled')

cmnds.add('away-enable', handle_awayenable, 'OPER')
examples.add('away-enable' , 'enable the away plugin', 'away-enable')

def handle_awaydisable(bot, ievent):
    """ away-disable .. disable away """
    awaydict.data['enable'] = 0
    awaydict.save()
    plugins.reload('gozerplugs', 'away')
    ievent.reply('away disabled')

cmnds.add('away-disable', handle_awaydisable, 'OPER')
examples.add('away-disable', 'disable the away plugin', 'away-disable')
tests.add('away-enable --chan #dunkbots', 'enabled').fakein(':dunker!mekker@127.0.0.1 PRIVMSG #dunkbots :&').fakein(':dunker!mekker@127.0.0.1 PRIVMSG #dunkbots :re').add('away-disable --chan #dunkbots', 'disabled')
