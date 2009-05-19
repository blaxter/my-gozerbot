# plugs/ignore.py
#
#

""" ignore users. """

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from gozerbot.commands import cmnds
from gozerbot.generic import getwho
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
from gozerbot.ignore import addignore, delignore, ignore
from gozerbot.tests import tests
from gozerbot.users import users

plughelp.add('ignore', 'ignore users for a certain time')

def handle_ignore(bot, ievent):

    """ ignore nick for number of seconds. """

    try:
        (nick, nrseconds) = ievent.args
        nrseconds = int(nrseconds)
    except ValueError:
        ievent.missing('<nick> <seconds>')
        return

    userhost = getwho(bot, nick)

    if not userhost:
        ievent.reply("can't get userhost of %s" % nick)
        return

    allowed = users.allowed(userhost, 'OPER', log=False)

    if allowed:
        ievent.reply("can't ignore OPER")
        return

    addignore(userhost, nrseconds)
    ievent.reply("ignoring %s for %s seconds" % (nick, nrseconds))
    
cmnds.add('ignore', handle_ignore, ['OPER', 'IGNORE'], speed=1)
examples.add('ignore', 'ignore <nick> <seconds> .. ignore <nick> for <seconds>', 'ignore test 3600')
tests.add('ignore bottest 3', 'bottest').add('ignore-del bottest')

def handle_ignoredel(bot, ievent):

    """ remove nick from ignore list. """

    try:
        nick = ievent.args[0]
    except IndexError:
        ievent.missing('<nick>')
        return

    userhost = getwho(bot, nick)

    if not userhost:
        ievent.reply("can't get userhost of %s" % nick)
        return

    if delignore(userhost):
        ievent.reply("ignore for %s removed" % nick)
    else:
        ievent.reply("can't remove ignore of %s" % nick)
        
cmnds.add('ignore-del', handle_ignoredel, ['OPER', 'IGNORE'])
examples.add('ignore-del', 'ignore-del <nick> .. unignore <nick>', 'ignore-del dunker')
tests.add('ignore bottest 1').add('ignore-del bottest', 'removed')

def handle_ignorelist(bot, ievent):

    """ show ignore list. """

    ievent.reply(str(ignore))
    
cmnds.add('ignore-list', handle_ignorelist, 'OPER')
examples.add('ignore-list', 'show ignore list', 'ignore-list')
tests.add('ignore bottest 1').add('ignore-list', 'bottest').add('ignore-del bottest')
