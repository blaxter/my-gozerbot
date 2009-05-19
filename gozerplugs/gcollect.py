# plugs/gcollect.py
#
#

""" run garbage collector """

__copyright__ = 'this file is in the public domain'

from gozerbot.periodical import periodical
from gozerbot.generic import rlog
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.persist.persiststate import PlugState
from gozerbot.plughelp import plughelp
import gc, time

plughelp.add('gcollect', 'help the garbage collector')

state = PlugState()
state.define('wait', 300)
state.define('enable', 0)

if state['enable']:
    gc.enable()
    rlog(10, 'gcollect', 'garbage collector enabled .. wait is %s' % state['wait'])

def shutdown():
    periodical.kill()

def gcollect():
    rlog(1, 'gcollect', 'running collector')
    gc.collect()
    time.sleep(5)
    gc.collect()
    time.sleep(5)
    gc.collect()

if state['enable']:
    pid = periodical.addjob(state['wait'], 0, gcollect)
else:
    pid = None

def handle_gcollectwait(bot, ievent):
    try:
        newwait = int(ievent.args[0])
    except (IndexError, ValueError):
        ievent.reply('gcollect wait is %s seconds' % state['wait'])
        return
    if newwait < 60:
        ievent.reply('min. number of seconds is 60')
        return
    state['wait'] = newwait
    state.save()
    if pid:
        periodical.changeinterval(pid, newwait)
    ievent.reply('gcollect wait set to %s' % state['wait'])

cmnds.add('gcollect-wait', handle_gcollectwait, 'OPER')
examples.add('gcollect-wait', 'set wait of garbage collector', \
'gcollect-wait 300')

def handle_gcollect(bot, ievent):
    gcollect()
    ievent.reply('collector runned')

cmnds.add('gcollect', handle_gcollect, 'OPER', threaded=True)
examples.add('gcollect', 'run garbage collector', 'gcollect')

def handle_gcollectenable(bot, ievent):
    global pid
    state['enable'] = 1
    state.save()
    pid = periodical.addjob(state['wait'], 0, gcollect)
    ievent.reply('gcollect enabled')

cmnds.add('gcollect-enable', handle_gcollectenable, 'OPER')
examples.add('gcollect-enable', 'enable the garbage collector', 'gcollect-enable')

def handle_gcollectdisable(bot, ievent):
    state['enable'] = 0
    state.save()
    periodical.kill()
    ievent.reply('gcollect disabled')

cmnds.add('gcollect-disable', handle_gcollectdisable, 'OPER')
examples.add('gcollect-disable', 'disable the garbage collector', 'gcollect-disable')
