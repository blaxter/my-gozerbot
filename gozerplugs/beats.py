# gozerplugs/beats.py
#
#

""" internet time .beats """

__copyright__ = 'this file is in the public domain'

from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
from gozerbot.plughelp import plughelp
from gozerbot.tests import tests
import time, math

plughelp.add('beats', 'show internet time')

def handle_beats(bot, ievent):
    """ beats .. show current internet time """
    beats = ((time.time() + 3600) % 86400) / 86.4
    beats = int(math.floor(beats))
    ievent.reply('@' + str(beats))

cmnds.add('beats', handle_beats, 'USER')
examples.add('beats', 'show current internet time', 'beats')
tests.add('beats' , '@')
