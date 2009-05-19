# plugs/tell.py
#
#

""" send the output of a command to <nick>. """

from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plugins import plugins
from gozerbot.plughelp import plughelp
from gozerbot.tests import tests

plughelp.add('tell', 'the tell command sends the output of a command to \
another user')

def handle_tell(bot, ievent):
    """ send output of command to another user """
    if ievent.msg:
        ievent.reply('tell can only be used in a channel')
        return 
    try:
        nick, cmnd = ievent.rest.split(' ', 1)
    except ValueError:
        ievent.missing('<nick> <command>')
        return
    ievent.txt = cmnd
    #if not plugins.woulddispatch(bot, ievent):
    #    ievent.reply("can't execute %s" % cmnd)
    #    return  
    result = plugins.cmnd(bot, ievent)
    if not result:
        ievent.reply("no result for %s" % cmnd)
        return
    ievent.reply("%s sends your this: " % ievent.nick, result, nick=nick, \
dot=True)
    ievent.reply("%s item(s) send" % len(result))

cmnds.add('tell', handle_tell, 'USER', threaded=True)
examples.add('tell', 'tell <nick> <command> .. send output of command to \
another user', 'tell dunker version')
tests.add('tell dunker version', 'GOZERBOT')
