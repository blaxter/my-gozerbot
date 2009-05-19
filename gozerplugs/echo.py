# plugs/echo.py
#
#

""" simple echo command """

__copyright__ = 'this file is in the public domain'

from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp

plughelp.add('echo', 'simply write back what you tell it')

def handle_echo(bot, ievent):
    """ say back what is being said """
    ievent.reply(ievent.rest)

cmnds.add('echo', handle_echo, 'USER')
examples.add('echo', "echo Hello World!", 'echo')

