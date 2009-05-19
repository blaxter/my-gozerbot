# plugs/to.py
#
#

""" send output to another user .. used in a pipeline """

__copyright__ = 'this file is in the public domain'

from gozerbot.commands import cmnds
from gozerbot.generic import getwho, waitforqueue
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
from gozerbot.tests import tests

plughelp.add('to', 'send the output to another user .. used in a pipeline')

def handle_to(bot, ievent):
    """ direct pipeline output to <nick> """
    if not ievent.inqueue:
        ievent.reply('use to in a pipeline')
        return
    try:
        nick = ievent.args[0]
    except IndexError:
        ievent.reply('to <nick>')
        return
    if nick == 'me':
        nick = ievent.nick
    if not getwho(bot, nick):
        ievent.reply("don't know %s" % nick)
        return
    result = waitforqueue(ievent.inqueue, 5)
    if result:
        ievent.reply("%s sends you this:" % ievent.nick, nick=nick)
        ievent.reply(result, nick=nick, dot=True)
        if len(result) == 1:
            ievent.reply('1 element sent')
        else:
            ievent.reply('%s elements sent' % len(result))
    else:
        ievent.reply('nothing to send')

cmnds.add('to', handle_to, 'USER', threaded=True)
examples.add('to', 'send pipeline output to another user', 'list | to dunker')
tests.add('list | to dunker')
