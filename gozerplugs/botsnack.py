# plugs/botsnack.py
#
#

""" eat it """

__copyright__ = 'this file is in the public domain'

from gozerbot.utils.generic import convertpickle
from gozerbot.datadir import datadir
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.persist.persist import PlugPersist
from gozerbot.plughelp import plughelp
import random, os

plughelp.add('botsnack', 'give the bot a snack')

## UPGRADE PART

def upgrade():
    convertpickle(datadir + os.sep + 'old' + os.sep + 'botsnacklist', \
datadir + os.sep  + "plugs" + os.sep + "botsnack" + os.sep + 'botsnacklist')

## END UPGRADE PART

bsl = PlugPersist('botsnacklist')

if not bsl.data:
    bsl = PlugPersist('botsnacklist')
    if not bsl.data:
        bsl.data = []

def handle_botsnack(bot, ievent):
    """ botsnack .. give botsnack reply """
    if bsl.data:
        result = random.choice(bsl.data)
        result = result.replace('<nick>', ievent.nick)
        result = result.replace('<host>', ievent.userhost)
        ievent.reply(result)
    else:
        ievent.reply('smikkel ;]')

cmnds.add('botsnack', handle_botsnack, ['USER', 'CLOUD'])
examples.add('botsnack', 'give the bot a snack ;] .. botsnack responses \
can be added with botsnack-add', 'botsnack')

def handle_addbotsnack(bot, ievent):
    """ botsnack-add <reply> .. add botsnack reply """
    if not ievent.rest:
        ievent.missing('<what>')
        return
    # append and save
    bsl.data.append(ievent.rest)
    bsl.save()
    ievent.reply('botsnack added')

cmnds.add('botsnack-add', handle_addbotsnack, 'OPER', allowqueue=False)
examples.add('botsnack-add', 'botsnack-add <what> .. add a botsnack \
response, <nick> can be used to show nick of user giving the command', \
'botsnack-add thnx <nick> ;]')

def handle_listbotsnack(bot, ievent):
    """ botscnack-list .. list botsnack replies """
    ievent.reply(str(bsl.data))

cmnds.add('botsnack-list', handle_listbotsnack, 'OPER')
examples.add('botsnack-list', 'show list of botsnack replies', 'botsnack-list')

def handle_delbotsnack(bot, ievent):
    """ botsnack-del <reply> .. delete botsnack reply """
    if not ievent.rest:
        ievent.missing('<txt>')
        return
    try:
        bsl.data.remove(ievent.rest)
        bsl.save()
    except ValueError:
        ievent.reply('i have no %s in botsnacklist' % ievent.rest)
        return
    ievent.reply('botsnack %s removed' % ievent.rest)

cmnds.add('botsnack-del', handle_delbotsnack, 'OPER')
examples.add('botsnack-del', 'delete entry from botsnack list', 'botsnack-del \
thnx <nick> ;]')
