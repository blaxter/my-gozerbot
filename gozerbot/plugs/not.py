# gozerbot/plugs/not.py
#
#

""" negative grep. """

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from gozerbot.tests import tests
from gozerbot.examples import examples
from gozerbot.commands import cmnds
from gozerbot.generic import waitforqueue
from gozerbot.plughelp import plughelp

# basic imports
import getopt, re

plughelp.add('not', 'the not command is a negative grep used in pipelines')

def handle_not(bot, ievent):

    """ negative grep. """

    if not ievent.inqueue:
        ievent.reply('use not in a pipeline')
        return

    if not ievent.rest:
        ievent.reply('not <txt>')
        return

    try:
        (options, rest) = getopt.getopt(ievent.args, 'r')
    except getopt.GetoptError, ex:
        ievent.reply(str(ex))
        return

    result = waitforqueue(ievent.inqueue, 10)

    if not result:
        ievent.reply('no data to grep on')
        return

    doregex = False

    for i, j in options:
        if i == '-r':
            doregex = True

    res = []

    if doregex:
        try:
            reg = re.compile(' '.join(rest))
        except Exception, ex:
            ievent.reply("can't compile regex: %s" % str(ex))
            return
        for i in result:
            if not re.search(reg, i):
                res.append(i)
    else:
        for i in result:
            if ievent.rest not in str(i):
                res.append(i)

    if not res:
        ievent.reply('no result')
    else:
        ievent.reply(res, dot=True)

cmnds.add('not', handle_not, ['USER', 'WEB', 'CLOUD'], threaded=True)
examples.add('not', 'reverse grep used in pipelines', 'list | not todo')
tests.add('list | not core')
