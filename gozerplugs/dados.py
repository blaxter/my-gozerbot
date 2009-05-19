# encoding: utf-8
from gozerbot.commands import cmnds

import re
import random

def instructions():
    return "Error: Use !dados or !dados SomeNumber (like !dados 10)"

def handle_dados(bot, ievent):
    n = -1
    if len(ievent.args) > 0:
        value = re.match("^([0-9]{0,6})$", str(ievent.args[0]))
        if value: n = int( value.group(1) )
    else:
        n = 100

    if n > 0:
        choice = random.choice( range(n+1) )
        ievent.reply( str( choice ) )
    else:
        ievent.reply( instructions() )

cmnds.add('dados', handle_dados, 'ANY')
