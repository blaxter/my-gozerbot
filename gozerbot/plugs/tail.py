# plugs/tail.py
#
#

""" tail bot results. """

__copyright__ = 'this file is in the public domain'

from gozerbot.generic import waitforqueue
from gozerbot.commands import cmnds
from gozerbot.plughelp import plughelp
from gozerbot.examples import examples
from gozerbot.tests import tests

plughelp.add('tail', 'show last <nr> elements of pipeline')

def handle_tail(bot, ievent):
    """ used in a pipeline .. show last <nr> elements """
    if not ievent.inqueue:
        ievent.reply("use tail in a pipeline")
        return
    try:
        nr = int(ievent.args[0])
    except (ValueError, IndexError):
        ievent.reply('tail <nr>')
        return
    result = waitforqueue(ievent.inqueue, 30)
    if not result:
        ievent.reply('no data to tail')
        return
    ievent.reply(result[-nr:])
    
cmnds.add('tail', handle_tail, ['USER', 'CLOUD'], threaded=True)
examples.add('tail', 'show last <nr> lines of pipeline output', \
'list | tail 5')
tests.add('list | tail 5')
