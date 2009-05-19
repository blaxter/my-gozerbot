# plugs/choice.py
#
#

""" the choice command can be used with a string or in a pipeline """

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from gozerbot.generic import waitforqueue
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
from gozerbot.tests import tests

# basic imports
import random

plughelp.add('choice', 'make a random choice')

def handle_choice(bot, ievent):

    """ make a random choice out of different words or list elements. """ 

    result = []

    if ievent.inqueue:
        result = waitforqueue(ievent.inqueue, 5)
    elif not ievent.args:
        ievent.missing('<space seperated list>')
        return
    else:
        result = ievent.args         

    ievent.reply(random.choice(result))

cmnds.add('choice', handle_choice, ['USER', 'WEB', 'CLOUD'], threaded=True)
examples.add('choice', 'make a random choice', '1) choice a b c 2) list | choice')
tests.add('choice a ab ac', 'a')
tests.add('list | choice')
