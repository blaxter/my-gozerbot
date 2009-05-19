# plugs/timer.py
#
#

__copyright__ = 'this file is in the public domain'

from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plugins import plugins
from gozerbot.plughelp import plughelp
import time

plughelp.add('timer', 'do a timing of a command')

def handle_timer(bot, ievent):
    """ do a timing of a command """
    if not ievent.rest:
        ievent.reply('<cmnd>')
        return
    ievent.txt = ievent.rest
    starttime = time.time()
    result = plugins.cmnd(bot, ievent, 60)
    stoptime = time.time()
    if not result:
        ievent.reply('no result for %s' % ievent.rest)
        return
    result.insert(0, "%s seconds ==>" % str(stoptime-starttime))
    ievent.reply('timer results: ', result)

cmnds.add('timer', handle_timer, ['USER', 'WEB'], allowqueue=False, \
threaded=True)
examples.add('timer', 'time a command', 'timer version')
