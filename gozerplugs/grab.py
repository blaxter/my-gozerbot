# plugs/grab.py

""" quotes grab plugin """

__copyright__ = 'this file is in the public domain'
__depend__ = ['quote', ]

from gozerbot.config import config
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.aliases import aliases
from gozerbot.plughelp import plughelp
from gozerplugs.quote import quotes

plughelp.add('grab', 'grab the last quote of an user')

def handle_quotegrab(bot, ievent):
    """ grab the last last from the given user """
    try:
        from gozerplugs.seen import seen
        assert(seen)
    except (ImportError, AssertionError, NameError):
        ievent.reply("seen plugin not enabled")
        return
    if not quotes:
        ievent.reply('quotes plugin not enabled')
        return
    if not ievent.args:
        ievent.reply('missing <user> argument')
        return
    nick = ievent.args[0].lower()
    if not seen.data.has_key(nick):
        ievent.reply('nothing said by %s recently' % nick)
        return
    idnr = quotes.add(nick, ievent.userhost, seen.data[nick]['text'])
    ievent.reply('grabbed %s from %s' % (idnr, nick))

cmnds.add('quote-grab', handle_quotegrab, ['USER', 'QUOTEADD'], allowqueue=False)
examples.add('quote-grab', 'quote-grab <user> .. add quote', 'quote-grab mekker')
aliases.data['grab'] = 'quote-grab'
