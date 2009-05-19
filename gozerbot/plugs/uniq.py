# gozerbot/plugs/uniq.py
#
# used in a pipeline .. unique elements """
# Wijnand 'tehmaze' Modderman - http://tehmaze.com
# BSD License

"""  used in a pipeline .. unique elements """

__author__ = "Wijnand 'tehmaze' Modderman - http://tehmaze.com"
__license__ = 'BSD'

from gozerbot.commands import cmnds
from gozerbot.generic import waitforqueue
from gozerbot.plughelp import plughelp
from gozerbot.tests import tests
import sets

plughelp.add('uniq', 'unique elements of a pipeline')

def handle_uniq(bot, ievent):
    """ uniq the result list """
    if not ievent.inqueue:
        ievent.reply('use uniq in a pipeline')
        return
    result = waitforqueue(ievent.inqueue, 30)
    if not result:
        ievent.reply('no data')
        return
    result = list(sets.Set(result))
    if not result:
        ievent.reply('no result')
    else:
        ievent.reply(result, dot=True)

cmnds.add('uniq', handle_uniq, ['USER', 'WEB', 'CLOUD'])
tests.add('list | uniq')
