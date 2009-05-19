# plugs/hello.py
#
#

__copyright__ = 'this file is in the public domain'

from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp

plughelp.add('hello', 'hello world like plugin (used as example)')

def handle_hello(bot, ievent):
    """ say hello nickname """
    ievent.reply('hello ' + ievent.nick)

cmnds.add('hello', handle_hello, 'USER')
examples.add('hello', "hello 'world' example", 'hello')

