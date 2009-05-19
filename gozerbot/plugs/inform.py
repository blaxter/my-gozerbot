# gozerbot/plugs/inform.py
#
#

""" prepend nick: to the output of a command. """

# gozerbot imports
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plugins import plugins
from gozerbot.plughelp import plughelp
from gozerbot.tests import tests

plughelp.add('inform', 'inform <nick> the output of a command')

def handle_inform(bot, ievent):
    """ prepend nick: to the output of command to another user """
    if ievent.msg:
        ievent.reply('inform can only be used in a channel')
        return
 
    try:
        nick, cmnd = ievent.rest.split(' ', 1)
    except ValueError:
        ievent.missing('<nick> <command>')
        return

    ievent.txt = cmnd
    result = plugins.cmnd(bot, ievent)

    if not result:
        ievent.reply("no result for %s" % cmnd)
        return

    ievent.reply("%s: " % nick, result, dot=True)

cmnds.add('inform', handle_inform, 'USER', threaded=True)
examples.add('inform', 'inform <nick> <command> .. inform <nick> the output of command', 'inform dunker version')
tests.add('inform dunker version', 'dunker')
