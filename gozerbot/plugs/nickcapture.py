# gozerplugs/plugs/nickcapture.py
#
#

""" nick recapture callback. """

__copyright__ = 'this file is in the public domain'

from gozerbot.callbacks import callbacks
from gozerbot.plughelp import plughelp

plughelp.add('nickcapture', 'nickcapture takes a nick back if a user quits')

def ncaptest(bot, ievent):

    """ test if user is splitted. """

    if '*.' in ievent.txt or bot.server in ievent.txt:
        return 0

    if bot.orignick.lower() == ievent.nick.lower():
        return 1

    return 0

def ncap(bot, ievent):

    """ recapture the nick. """

    bot.donick(bot.orignick)

callbacks.add('QUIT', ncap, ncaptest, threaded=True)
