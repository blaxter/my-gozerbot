# gozerplugs/plugs/rest.py
#
#

__author__ = "Wijnand 'tehmaze' Modderman - http://tehmaze.com"
__license__ = 'BSD'

from gozerbot.commands import cmnds
from gozerbot.plughelp import plughelp
from gozerbot.examples import examples
from gozerbot.tests import tests
import time

plughelp.add('rest', 'show rest of the output in /msg')

def handle_rest(bot, ievent):
    """ show rest of the output in /msg """
    try:
        who = ievent.args[0]
    except IndexError:
        if bot.jabber:
            who = ievent.userhost
        else:
            who = ievent.nick
    what, size = bot.less.more(who, 0)
    if not what:
        ievent.reply('no more data available for %s' % who)
        return
    if not bot.jabber and int(size)+1 > 10:
        ievent.reply("showing %d of %d lines in private" % \
(10, int(size)+1))
    else:
        ievent.reply("showing %d lines in private" % (int(size)+1))
    count = 0
    while what:
        count += 1
        if bot.jabber:
            if size:
                bot.say(ievent.userhost, "%s (+%s)" % (what, size))
            else:
                bot.say(ievent.userhost, what)
        else:
            if size:
                bot.output(ievent.nick, "%s (+%s)" % (what, size))
            else:
                bot.output(ievent.nick, what)
        # output limiter
        if count >= 10:
            what = None
        else:
            what, size = bot.less.more(who, 0)
            if what:
                time.sleep(3)
    # let the user know if we have remaining data
    if size:
        s = ''
        if size > 1:
            s = 's'
        if bot.jabber:
            bot.say(ievent.userhost, "%s more line%s" % (size, s)) 
        else:
            bot.output(ievent.nick, "%s more line%s" % (size, s))

cmnds.add('rest', handle_rest, 'USER')
examples.add('rest', 'show the rest of output cache data', 'rest')
tests.add('avail | rest')
