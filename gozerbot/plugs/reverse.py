# gozerplugs/plugs/reverse.py
#
# 

__copyright__ = 'this file is in the public domain'
__author__ = 'Hans van Kranenburg <hans@knorrie.org>'

from gozerbot.generic import waitforqueue
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
from gozerbot.tests import tests

plughelp.add('reverse', 'reverse string or list')

def handle_reverse(bot, ievent):
    """ reverse string or pipelined list """
    if ievent.inqueue:
        result = waitforqueue(ievent.inqueue, 5)
    elif not ievent.rest:
        ievent.missing('<text to reverse>')
        return
    else:
        result = ievent.rest
    ievent.reply(result[::-1])

cmnds.add('reverse', handle_reverse, ['USER', 'CLOUD'], threaded=True)
examples.add('reverse', 'reverse text or pipeline', '1) reverse gozerbot 2) list | \
reverse')
tests.add('reverse gozerbot', 'tobrezog').add('list | reverse', 'misc')
