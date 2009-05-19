# plugs/jabber.py
#
#

""" jabber related commands. """

__copyright__ = 'this file is in the public domain'

# gozerbot import
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp

plughelp.add('jabber', 'jabber specific commands')

def handle_jabberratelimit(bot, ievent):

    """ set jabber output limiter. """

    if not bot.jabber:
        ievent.reply('this command only works on a jabber bot')
        return 

    try:
        limit = int(ievent.args[0])
    except IndexError:
        ievent.reply('limiter is %s seconds' % bot.state['ratelimit'])
        return
    except ValueError:
        ievent.missing('<seconds>')
        return

    bot.state['ratelimit'] = limit
    ievent.reply('rate limiter set to %s' % limit)

cmnds.add('jabber-ratelimit', handle_jabberratelimit, 'OPER')
examples.add('jabber-ratelimit', 'limit jabber output', 'jabber-ratelimit 1')

def handle_ircstr(bot, ievent):

    """ show ircevent repr like string of jabbermessage. """

    if not bot.jabber:
        ievent.reply('this command only works on a jabber bot')
        return 

    ievent.reply(ievent.ircstr())

cmnds.add('jabber-ircstr', handle_ircstr, 'OPER')
examples.add('jabber-ircstr', 'show the given event as ircstr', 'jabber-ircstr')
