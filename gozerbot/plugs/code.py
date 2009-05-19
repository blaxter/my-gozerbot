# plugs/code.py
#
#

""" code related commands. """

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from gozerbot.redispatcher import rebefore, reafter
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.generic import exceptionlist
from gozerbot.plugins import plugins
from gozerbot.aliases import aliasset
from gozerbot.plughelp import plughelp
from gozerbot.tests import tests

plughelp.add('code', 'the code plugin provides code related commands')

def handle_showexceptions(bot, ievent):

    """ show exception list. """

    ievent.reply(str(exceptionlist))

cmnds.add('code-exceptions' , handle_showexceptions, 'OPER')
examples.add('code-exceptions', 'show exception list', 'code-exceptions')
aliasset('exceptions', 'code-exceptions')
tests.add('code-exceptions')

def handle_funcnames(bot, ievent):

    """ show function names of a plugin. """

    try:
        plugname = ievent.args[0]
    except IndexError:
        ievent.missing('<plugname>')
        return

    if not plugins.exist(plugname):
        ievent.reply('no %s plugin exists' % plugname)
        return

    funcnames = []
    funcnames = rebefore.getfuncnames(plugname)
    funcnames += cmnds.getfuncnames(plugname)
    funcnames += reafter.getfuncnames(plugname)

    if funcnames:
        ievent.reply(funcnames, dot=True)
    else:
        ievent.reply("can't find funcnames for %s plugin" % plugname)
        
cmnds.add('code-funcnames', handle_funcnames, 'OPER')
examples.add('code-funcnames', 'show function names of a plugin', 'code-funcnames birthday')
aliasset('funcnames', 'code-funcnames')
tests.add('code-funcnames core', 'handle_version')
