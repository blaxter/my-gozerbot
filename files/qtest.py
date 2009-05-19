#!/usr/bin/env python
#
# copy this script to the botdir

__copyright__ = 'this file is in the public domain'

donot = ['reboot', 'cycle', 'loglevel', 'quit', 'email', 'meet', 'nick', \
'part', 'cc', 'chat', 'join', ' nick', 'update', 'install', \
'reconnect', 'jump', 'nonfree', 'relay', 'rss', 'fleet', 'sendraw', \
'upgrade', 'alarm', 'remind', 'intro', 'host', 'ip', 'alarm', 'tests', \
'unload', 'delete', 'dfwiki', 'dig', 'silent', 'reconnect', 'switch', 'op',
'dict', 'slashdot', 'films', 'latest', 'weather', 'coll', 'web', 'mail', \
'markov', 'probe']

from gozerbot.users import users
from gozerbot.examples import examples
from gozerbot.plugins import plugins
from gozerbot.bot import Bot
from gozerbot.ircevent import Ircevent
from gozerbot.generic import handle_exception, die
from gozerbot.config import config
import gozerbot.thr as thr
config['loglevel'] = 100

import Queue, signal, time, random, sys
sys.setcheckinterval(1000)
nrtimes = 10

try:
    nrtimes = int(sys.argv[1])
except:
    pass

def stop(x, y):
    tmpstr =  '\nremaining: '
    teller = 0
    for i in queues:
        teller += 1
        tmpstr += "%s) %s " % (teller, i[2])
    print tmpstr
    die()

# register SIGTERM handler to stop
signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)

try:
    users.delete('test')
except:
    pass

users.add('test', ['test@test', ], ['USER', 'OPER', 'ALIAS', 'FORGET', \
'QUOTE'])

bot = Bot('test@test')
bot.channels.data['#dunkbots'] = {}
bot.userhosts['dunker'] = 'test@test'
print "loading plugins"
plugins.regplugins()

queues = []

def qreader():
    while 1:
        time.sleep(0.01)
        for i in queues:
            (testnr, teller, cmnd, q) = i
            try:
                res = q.get(1, 1)
                nr = len(queues)
                print '\n<=%s==%s=> (%s)' % (testnr, teller, nr)
                print "%s => %s" % (cmnd, res)
                queues.remove((testnr, teller, cmnd, q))
            except:
                pass
        
def dotest(testnr):
    exs = examples.getexamples()
    random.shuffle(exs)
    teller = 0
    for i in exs:
        no = 0
        for zz in donot:
            if i.find(zz) != -1:
                no = 1
                break
        if no:
            continue
        teller += 1
        try:
            ievent = Ircevent()
            ievent.nick = 'test'
            ievent.userhost = 'test@test'
            q = Queue.Queue()
            ievent.queues.append(q)
            ievent.channel = '#dunkbots'
            ievent.txt = i
            queues.append((testnr, teller, i, q))
            if not plugins.trydispatch(bot, ievent):
                print "\ncan't execute %s\n" % i
                queues.remove((testnr, teller, i, q))
        except:
            handle_exception()

thr.start_new_thread(qreader, ())

for a in range(nrtimes):
    thr.start_new_thread(dotest, (a, ))

while 1:
    time.sleep(1)
