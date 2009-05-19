# plugs/chanperm.py
#
#

""" allow all user in a channel to have permissions. permission that use 
userstate information can not be used, for that the users must be meeted to 
the bot.
"""

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
from gozerbot.utils.log import rlog
from gozerbot.tests import tests

plughelp.add('chanperm', 'manage channel permissions')

def handle_chanperm(bot, ievent):

    """ show channel permissions. """

    chan = ievent.channel.lower()

    try:
        p = bot.channels[chan]['perms']
    except (KeyError, TypeError):
        ievent.reply("channel %s has no permissions set" % chan)
        return

    if p:
        ievent.reply('permissions of channel %s: ' % chan, p, dot=True)
    else:
        ievent.reply("channel %s has no permissions set" % chan)
    
cmnds.add('chanperm', handle_chanperm, 'OPER')
examples.add('chanperm', 'show channel permissions', 'chanperm')
tests.add('chanperm-add mekker chan #dunkbots').add('chanperm chan #dunkbots', 'MEKKER').add('chanperm-del chan #dunkbots mekker')

def handle_chanpermadd(bot, ievent):

    """ add channel permission. """

    try:
        perm = ievent.args[0].upper()
    except IndexError:
        ievent.missing('<perm>')
        return

    if perm in ['OPER', 'USER']:
        ievent.reply("can't set channel permission to %s" % perm)
        return

    chan = ievent.channel.lower()

    try:
        if perm in bot.channels[chan]['perms']:
            ievent.reply('channel %s already has %s permission set' % \
(chan, perm))
            return
    except (KeyError, TypeError):
        try:
            bot.channels[chan].setdefault('perms', [])
        except AttributeError:
            ievent.reply('channel %s is not in channel database' % chan)
            return

    bot.channels[chan]['perms'].append(perm.upper())
    bot.channels.save()
    ievent.reply('%s channel perm added' % perm)
    
cmnds.add('chanperm-add', handle_chanpermadd, 'OPER', allowqueue=False)
examples.add('chanperm-add', 'add channel permission <perm>', 'chanperm-add ANONKARMA')
tests.add('chanperm-add mekker chan #dunkbots', 'MEKKER').add('chanperm-del mekker chan #dunkbots')

def handle_chanpermdel(bot, ievent):

    """ delete channel permission. """

    try:
        perm = ievent.args[0]
    except IndexError:
        ievent.missing('<perm>')
        return

    chan = ievent.channel.lower()

    try:
        bot.channels[chan]['perms'].remove(perm.upper())
        ievent.reply('%s channel perm deleted' % perm)
    except (ValueError, KeyError, TypeError):
        ievent.reply('there is no %s permission for channel %s' % (perm, chan))

cmnds.add('chanperm-del', handle_chanpermdel, 'OPER')
examples.add('chanperm-del', 'delete channel permission <perm>', 'chanperm-del ANONKARMA')
tests.add('chanperm-add mekker chan #dunkbots').add('chanperm-del mekker chan #dunkbots', 'mekker')
