# plugins/autoreply.py
#
#

""" do autoreply on incoming jabber private messages except commands. to enable
 use autoreply-cfg txt <message to send>. """

__copyright__ = 'this file is in the public domain'

from gozerbot.commands import cmnds
from gozerbot.callbacks import jcallbacks
from gozerbot.aliases import aliasset
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.plughelp import plughelp
from gozerbot.examples import examples
from gozerbot.tests import tests

cfg = PersistConfig()
cfg.define('txt', "")

plughelp.add('autoreply', 'jabber autoreply')

def preautoreply(bot, ievent):
    """ check where autoreply callbacks should fire """
    if not ievent.usercmnd and cfg.get('txt') and not ievent.groupchat:
        return 1

def cbautoreply(bot, ievent):
    """ do the auto reply """
    bot.say(ievent.userhost, cfg.get('txt'))

jcallbacks.add('Message', cbautoreply, preautoreply)

def handle_autoreplydisable(bot, ievent):
    """ disable autoreply """
    cfg.set('txt', '')
    ievent.reply('autoreply is disabled')
    
cmnds.add('autoreply-disable', handle_autoreplydisable, 'OPER')
examples.add('autoreply-disable', 'disable the autoreply functionality', \
'autoreply-disable')

aliasset('autoreply-set', 'autoreply-cfg txt')
aliasset('autoreply-enable', 'autoreply-cfg txt')
tests.add('autoreply-enable mekker', 'set').add('autoreply-disable')
