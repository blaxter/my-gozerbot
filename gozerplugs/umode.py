# plugs/umode.py
# 
#

__author__ = "Wijnand 'tehmaze' Modderman - http://tehmaze.com"
__license__ = 'BSD'
__gendoclast__ = ['usermode-del', ]

from gozerbot.utils.generic import convertpickle
from gozerbot.callbacks import callbacks
from gozerbot.commands import cmnds
from gozerbot.datadir import datadir
from gozerbot.persist.pdol import Pdol
from gozerbot.plughelp import plughelp
from gozerbot.examples import examples
import os
import types

plughelp.add('umode', 'on-connect bot usermode')

## UPGRADE PART

def upgrade():
    convertpickle(datadir + os.sep + 'umode', datadir + os.sep + 'plugs' + os.sep + 'umode' + \
os.sep + 'umode')

## END UPGRADE PART

class UModes(Pdol):

    """ umodes object """

    def __init__(self):
        Pdol.__init__(self, datadir + os.sep + 'plugs' + os.sep + 'umode' + \
os.sep + 'umode')

    def addmode(self, bot, modes):
        """ add a mode to the bot """
        if type(modes) == types.StringType:
            modes = list(modes)
        if not self.get(bot.name):
            self.new(bot.name)
        for mode in modes:
            if not mode in self.data[bot.name]:
                self.add(bot.name, mode)
        self.save()

    def delmode(self, bot, modes):
        """ delete mode from the bot """
        if type(modes) == types.StringType:
            modes = list(modes)
        if not self.get(bot.name):
            return
        for mode in modes:
            if mode in self.data[bot.name]:
                self.data[bot.name].remove(mode)
        self.save()

    def getmode(self, bot):
        """ get mode of the bot """
        return self.get(bot.name) or []

    def domode(self, bot):
        """ set bot mode on server """
        modes = self.getmode(bot)
        if modes:
            bot.sendraw('MODE %s +%s' % (bot.nick, ''.join(modes)))

    def handle_001(self, bot, ievent):
        """ call on connect to server """
        self.domode(bot)

umodes = UModes()
if not umodes.data:
    umodes = UModes()

def handle_usermodeadd(bot, ievent):
    """ add mode to bot """
    if not ievent.args:
        ievent.missing('<mode(s)>')
        return
    umodes.addmode(bot, ' '.join(ievent.args).replace(' ', ''))
    umodes.domode(bot)
    ievent.reply('ok')

cmnds.add('usermode-add', handle_usermodeadd, 'OPER', threaded=True)
examples.add('usermode-add', 'add a usermode', 'usermode-add I')

def handle_usermodedel(bot, ievent):
    """ delete mode from bot """
    if not ievent.args:
        ievent.missing('<mode(s)>')
        return
    modes = list(' '.join(ievent.args).replace(' ', ''))
    umodes.delmode(bot, modes)
    bot.sendraw('MODE %s -%s' % (bot.nick, ''.join(modes)))
    ievent.reply('ok')

cmnds.add('usermode-del', handle_usermodedel, 'OPER', threaded=True)
examples.add('usermode-del', 'remove a usermode', 'usermode-del I')

def handle_usermodelist(bot, ievent):
    """ list modes of bot """
    modes = umodes.getmode(bot)
    if not modes:
        ievent.reply('no modes set')
    else:
        modes.sort()
        ievent.reply('mode +%s' % ''.join(modes))

cmnds.add('usermode-list', handle_usermodelist, 'OPER')
examples.add('usermode-list', 'show user modes', 'usermode-list')

# callbacks
callbacks.add('001', umodes.handle_001)
