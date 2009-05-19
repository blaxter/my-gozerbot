#!/usr/bin/env python
#
# copy this script to the botdir

__copyright__ = 'this file is in the public domain'

from gozerbot.users import users
from gozerbot.plugins import plugins
from gozerbot.bot import Bot
from gozerbot.ircevent import Ircevent
from gozerbot.generic import handle_exception, die
from gozerbot.config import config
import gozerbot.thr as thr
config['loglevel'] = 10
import Queue, signal, time, sys, os
nrtimes = 10
hammers = 10

try:
    nrtimes = int(sys.argv[1])
    nail = ' '.join(sys.argv[2:])
except:
    print 'hammer.py <nrtimes> <command>'
    os._exit(0)

def stop(x, y):
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
plugins.regplugins()
time.sleep(5)

queues = []

def qreader():
    while 1:
        for i in queues:
            time.sleep(0.01)
            try:
                (cmnd, q) = i
                res = q.get_nowait()
                print "%s => %s" % (cmnd, res)
                queues.remove(i)
            except:
                pass
            
def dohammer():
    for j in range(nrtimes):
        try:
            ievent = Ircevent()
            ievent.nick = 'test'
            ievent.userhost = 'test@test'
            q = Queue.Queue()
            ievent.queue = q
            ievent.channel = '#dunkbots'
            ievent.txt = nail
            queues.append((nail, q))
            if not plugins.trydispatch(ievent):
                print "\ncan't execute %s\n" % nail
                queues.remove((nail, q))
        except:
            handle_exception()

thr.start_new_thread(qreader, ())
thr.start_new_thread(dohammer, ())

while 1:
    time.sleep(1)
