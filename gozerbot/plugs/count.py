# plugs/count.py
#
#

""" count number of items in result queue. """

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from gozerbot.commands import cmnds
from gozerbot.generic import waitforqueue
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
from gozerbot.tests import tests

plughelp.add('count', 'the count command counts the number of results in a \
pipeline')

def handle_count(bot, ievent):

    """ show nr of elements in result list. """

    if not ievent.inqueue:
        ievent.reply("use count in a pipeline")
        return

    result = waitforqueue(ievent.inqueue, 5)
    ievent.reply(str(len(result)))

cmnds.add('count', handle_count, ['USER', 'WEB', 'CLOUD'], threaded=True)
examples.add('count', 'count nr of items', 'todo | count')
tests.add('list | count')
