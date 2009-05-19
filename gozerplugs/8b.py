# plugs/8b.py
#
#
#

""" eight ball """

__copyright__ = 'this file is in the public domain'
__revision__ = '$Id: m8b.py 1120 2006-12-30 12:00:00Z deck $'

from gozerbot.generic import handle_exception
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
from gozerbot.tests import tests
import re, random

plughelp.add('8b', 'Ask the magic 8 ball')

balltxt=[
    "Signs point to yes.",
    "Yes.",
    "Most likely.",
    "Without a doubt.",
    "Yes - definitely.",
    "As I see it, yes.",
    "You may rely on it.",
    "Outlook good.",
    "It is certain.",
    "It is decidedly so.",
    "Reply hazy, try again.",
    "Better not tell you now.",
    "Ask again later.",
    "Concentrate and ask again.",
    "Cannot predict now.",
    "My sources say no.",
    "Very doubtful.",
    "My reply is no.",
    "Outlook not so good.",
    "Don't count on it."
    ]

def handle_8b(bot, ievent):
    ievent.reply(random.choice(balltxt))

cmnds.add('8b', handle_8b, 'USER')
examples.add('8b', 'show what the magic 8 ball has to say', '8b')
tests.add('8b')
