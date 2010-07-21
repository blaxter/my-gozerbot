# encoding: utf-8
from gozerbot.commands import cmnds

from random import random

def random_char(what, min, max):
    return what * (min + int(random() * max))

def handle_vuvuzela(bot, ievent):
    ievent.reply( random_char('b', 5, 25) + random_char('z', 5, 25) )

cmnds.add('vuvuzela', handle_vuvuzela, 'ANY')
