# plugs/size.py
#
#

""" show sizes of plugin data. """

__copyright__ = 'this file is in the public domain'

from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.users import users
from gozerbot.redispatcher import rebefore, reafter
from gozerbot.aliases import aliases
from gozerbot.callbacks import callbacks
from gozerbot.plugins import plugins
from gozerbot.fleet import fleet
from gozerbot.plughelp import plughelp
from gozerbot.tests import tests

plughelp.add('size', 'the size command shows the sizes of plugins that \
provide a size() plugin command and the sizes of some basic structures')

def handle_size(bot, ievent):
    """ size .. show size of core datastructures """
    txtlist = []
    txtlist.append("fleet: %s" % fleet.size())
    txtlist.append("users: %s" % users.size())
    txtlist.append("cmnds: %s" % cmnds.size())
    txtlist.append("callbacks: %s" % callbacks.size())
    txtlist.append("rebefore: %s" % rebefore.size())
    txtlist.append("reafter: %s" % reafter.size())
    txtlist.append("aliases: %s" % len(aliases.data))
    txtlist.append("examples: %s" % examples.size()) 
    plugsizes = plugins.plugsizes()
    if plugsizes:
        txtlist += plugsizes
    ievent.reply(txtlist)

cmnds.add('size', handle_size, ['USER', 'WEB'])
examples.add('size', 'show sizes of various data structures', 'size')
tests.add('size', 'users')
