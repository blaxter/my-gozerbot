# gozerbot/plugs/stats.py
#
#

from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.stats import stats
from gozerbot.tests import tests

def handle_stats(bot, ievent):
    if not ievent.rest:
        ievent.missing('[%s]' % '|'.join(stats.all()))
        return
    item = ievent.rest
    result = stats.get(item)
    if result:
        ievent.reply('stats of %s ==> ' % item, dict(result))

cmnds.add('stats', handle_stats, 'OPER')
