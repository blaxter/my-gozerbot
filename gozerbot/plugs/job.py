# gozerbot/plugs/job.py
#
# (c) Wijnand 'tehmaze' Modderman - http://tehmaze.com
# BSD License

""" job management. """

__author__ = "Wijnand 'tehmaze' Modderman - http://tehmaze.com"
__license__ = "BSD"

# gozerbot imports
from gozerbot.aliases import aliases
from gozerbot.commands import cmnds
from gozerbot.periodical import periodical, at
from gozerbot.plugins import plugins
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
from gozerbot.generic import uniqlist
from gozerbot.tests import tests

# basic imports
import copy, datetime, time, types

plughelp.add('job', 'job management')

def size():

    """ show nr of running jobs. """

    return len(periodical.jobs)

def handle_job(bot, ievent):

    """ show data of <jobid>. """

    if not ievent.args or not ievent.args[0].isdigit():
        ievent.reply('<job id>')
        return

    for job in periodical.jobs:
        if job.id() == int(ievent.args[0]):
            next = job.next
            if type(next) in [types.FloatType, types.IntType]:
                next = datetime.datetime(*time.localtime(next)[:7])
            ievent.reply('%s, fires at %s' % (job.__repr__(), str(next)))
            return

    ievent.reply('job not found')

cmnds.add('job', handle_job, 'USER')
examples.add('job', 'show job data of <jobid> ', 'job 1')
tests.add('job 1')

def handle_joblist(bot, ievent):

    """ show job list. """

    try:
        group = ievent.args[0]
    except IndexError:
        group = None
    result = []

    for job in periodical.jobs:
        if group and not job.group == group:
            continue
        if job.description:
            result.append('%d (%s)' % (job.id(), job.description))
        else:
            result.append('%d (%s)' % (job.id(), str(job.func.func_name)))

    if result:
        ievent.reply('jobs scheduled: ', result, dot=True)
    else:
        ievent.reply('no jobs')

cmnds.add('job-list', handle_joblist, 'OPER')
examples.add('job-list', 'show all waiting jobs or all jobs belonging to [group]', '1) job-list 2) job-list rss')
aliases.data['jobs'] = 'job-list'
tests.add('job-list', 'cleanall')

def handle_jobgroups(bot, ievent):

    """ show job groups. """

    result = [job.group for job in periodical.jobs]

    if result:
        ievent.reply('job groups: ', uniqlist(result), dot=True)
    else:
        ievent.reply('no jobs')

cmnds.add('job-groups', handle_jobgroups, 'OPER')
examples.add('job-groups', 'show all job groups', 'job-groups')
tests.add('job-groups')

def handle_jobkill(bot, ievent):

    """ kill a job. """

    if not ievent.args or not ievent.args[0].isdigit():
        ievent.missing('<job id> [<job id> ...]')
        return

    try:
        ids = [int(jid) for jid in ievent.args]
    except ValueError:
        ievent.missing('<job id> [<job id> ...]')
        return

    for jid in ids:
        periodical.killjob(int(ievent.args[0]))

    ievent.reply('killed %d jobs' % len(ids))

cmnds.add('job-kill', handle_jobkill, 'OPER')
examples.add('job-kill', 'kill job with <jobid>', 'job-kill 100000')
