# plugs/at.py
#
#

""" run a bot command at a certain time. """

__author__ = "Wijnand 'tehmaze' Modderman - http://tehmaze.com"
__license__ = "BSD"

# gozerbot imports
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.periodical import at, periodical, JobError
from gozerbot.plugins import plugins
from gozerbot.irc.ircevent import Ircevent
from gozerbot.plughelp import plughelp
from gozerbot.tests import tests

# basic imports
import copy, types, time

plughelp.add('at', 'schedule a command at a specific time')

class AtJob:

    """ Job to run at certain time. """

    def __init__(self, when, bot, nevent):
        self.when = when
        self.bot  = bot
        self.nevent = nevent

        @at(when)
        def at_job():
            plugins.trydispatch(self.bot, self.nevent)
        at_job.cmnd = self.nevent.txt
        at_job.ievent = self.nevent
        at_job()

def handle_at(bot, ievent):

    """ start a job at a certain time. """

    if len(ievent.args) < 2:
        ievent.missing('<time> <command>')
        return

    nevent = Ircevent()
    nevent.copyin(ievent)
    nevent.txt = ' '.join(ievent.args[1:])
    nevent.origtxt = u'!' + nevent.txt

    if plugins.woulddispatch(bot, nevent):
        try:
            when = int(ievent.args[0])
        except ValueError, e:
            when = ievent.args[0] 
        try:
            AtJob(when, bot, nevent)
        except JobError:
            ievent.reply('wrong date/time')
            return
        ievent.reply('job scheduled')
    else:
        ievent.reply('could not dispatch')

cmnds.add('at', handle_at, 'USER')
examples.add('at', 'start a job at given time', 'at 23:00 say moooo')
tests.add('at 23:55 say #dunkbots mekker', 'job scheduled')

def handle_atlist(bot, ievent):

    """ show scheduled at events. """

    reply = []

    for job in periodical.jobs:
        if job.func.func_name != 'at_job':
            continue
        next = job.next
        if type(next) in [types.FloatType, types.IntType]:
            next = float(next)
        try:
            cmnd = job.func.cmnd
        except AttributeError:
            cmnd = '<unknown>'
        reply.append('%d: at %s, "%s"' % (job.id(), time.ctime(next), cmnd)) 

    if reply:
        ievent.reply(reply, dot=True)
    else:
        ievent.reply('no jobs')

cmnds.add('at-list', handle_atlist, 'OPER')
examples.add('at-list', 'show list of at jobs', 'at-list')
tests.add('at 23:59 version').add('at-list', 'version')
