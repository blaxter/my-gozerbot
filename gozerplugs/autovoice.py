# plugins/autovoice.py
#
#

""" do voice on join """

__copyright__ = 'this file is in the public domain'

from gozerbot.commands import cmnds
from gozerbot.callbacks import callbacks
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
from gozerbot.tests import tests

plughelp.add('autovoice', 'enable auto voicing of people join .. commands \
work for the channels the commands are given in')

def preautovoice(bot, ievent):
    """ precondition on auto-op .. we must be op """
    if ievent.channel in bot.state['opchan']:
        return 1

def cbautovoice(bot, ievent):
    """ autovoice callback """
    chandata = 0
    try:
        chandata = bot.channels[ievent.channel]['autovoice']
    except KeyError:
        return
    if chandata:
        bot.voice(ievent.channel, ievent.nick)

callbacks.add('JOIN', cbautovoice, preautovoice)

def handle_autovoiceon(bot, ievent):
    """ autovoice-on .. enable autovoice for channel the command was given \
        in """
    try:
        bot.channels[ievent.channel]['autovoice'] = 1
    except TypeError:
        ievent.reply('no %s in channel database' % ievent.channel)
        return
    ievent.reply('autovoice enabled on %s' % ievent.channel)

cmnds.add('autovoice-on', handle_autovoiceon, 'OPER')
examples.add('autovoice-on', 'enable autovoice on channel in which the \
command is given', 'autovoice-on')

def handle_autovoiceoff(bot, ievent):
    """ autovoice-off .. disable autovoice for the channel the command was \
        given in """
    bot.channels[ievent.channel]['autovoice'] = 0
    ievent.reply('autovoice disabled on %s' % ievent.channel)

cmnds.add('autovoice-off', handle_autovoiceoff, 'OPER')
examples.add('autovoice-off', 'disable autovoice on channel in which \
the command is given', 'autovoice-off')
tests.add('autovoice-on --chan #dunkbots', 'enabled').fakein(':dunker!mekker@127.0.0.1 JOIN #dunkbots').add('autovoice-off --chan #dunkbots', 'disabled')
