# gozerplugs/plugs/all.py
#
#

""" allow commands for all users. """

__gendoclast__ = ['all-del', ]

# gozerbot imports
from gozerbot.commands import cmnds
from gozerbot.aliases import aliasget
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
from gozerbot.tests import tests

plughelp.add('all', 'allow commands to be executed by all users')

def handle_alladd(bot, ievent):

    """ add a command to the allow all list. """

    if not ievent.rest:
        ievent.missing('<command>')
        return

    target = aliasget(ievent.rest) or ievent.rest

    if not 'OPER' in cmnds.perms(target):
        bot.state['allowed'].append(target)
        bot.state.save()
        ievent.reply('%s command is now allowed for all clients' % target)
    else:
        ievent.reply('sorry')

cmnds.add('all-add', handle_alladd, 'OPER')
examples.add('all-add', 'add command to be allowed by all users', 'all-add version')
tests.add('all-add version', 'version').add('all-del version')

def handle_alldel(bot, ievent):

    """ remove a command from the all allowed list. """

    if not ievent.rest:
        ievent.missing('<command>')
        return

    target = aliasget(ievent.rest) or ievent.rest

    if target in bot.state['allowed']:
        bot.state['allowed'].remove(target)
        ievent.reply('%s command is removed from allowed list' % target)
    else:
        ievent.reply('%s command is not in allowed list' % target)

cmnds.add('all-del', handle_alldel, 'OPER')
examples.add('all-del', 'remove command from the allowed list', 'all-del version')
tests.add('all-add version').add('all-del version', 'version')

def handle_alllist(bot, ievent):

    """ show the all allowed list. """

    ievent.reply('commands allowed: ', bot.state['allowed'], dot=True)

cmnds.add('all-list', handle_alllist, 'USER')
examples.add('all-list', 'list commands allowed by all users', 'all-list')
tests.add('all-add version').add('all-list', 'version').add('all-del version')
