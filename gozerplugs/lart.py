# gozerplugs/lart.py
#
#

from gozerbot.commands import cmnds
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.aliases import aliasset
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
import random

plughelp.add('lart', 'do the lart')

cfg = PersistConfig()
cfg.define('lartlist', [])

def handle_lart(bot, ievent):
    try:
        who = ievent.args[0]
    except IndexError:
        ievent.missing('<who>')
        return
    try:
        txt = random.choice(cfg.get('lartlist'))
    except IndexError:
        ievent.reply('lart list is empty .. use lart-add to add entries .. use "<who>" as a nick holder')
        return
    txt = txt.replace('<who>', who)
    bot.action(ievent.channel, txt)

cmnds.add('lart', handle_lart, 'USER')
examples.add('lart', 'echo a lart message', 'lart dunker')
aliasset('lart-add', 'lart-cfg lartlist add')
aliasset('lart-del', 'lart-cfg lartlist remove')
