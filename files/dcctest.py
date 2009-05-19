#!/usr/bin/env python
#
# copy this script to the botdir,edit and run it
# example: dcctest.py 10 0 .. this starts 10 test clients and sleep 0 sec
# between commands

__copyright__ = 'this file is in the public domain'

# vars
channel = '#dunkbots'
botnick = 'gozerbot'
mynick = 'test'
listenip = '127.0.0.1'
server = 'localhost'
port = 50002

# imports
from gozerbot.generic import handle_exception, rlog, enable_logging, setdefenc
from  gozerbot.config import config
enable_logging()
rlog(100, 'dcctest', 'starting...')
config['loglevel'] = 10
from gozerbot.plugins import plugins
from gozerbot.examples import examples
import gozerbot.generic
import gozerbot.bot
import gozerbot.irc
import sys, time, socket, thread, struct, os, random, signal
setdefenc('utf-8')
nrloops = 10
commandsdone = 0
starttime = time.time()

if not len(sys.argv) ==  4:
    print 'i need three  arguments: 1) nrloops 2) nrclients 3) timetosleep'
    os._exit(0)
else:
    nrloops = int(sys.argv[1])
    nrbots = int(sys.argv[2])
    timetosleep = float(sys.argv[3])

def stop(x, y):
    print str(commandsdone/(time.time()-starttime)) + " commands per second"
    gozerbot.generic.die()

# register SIGTERM handler to stop
signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)

plugins.regplugins()

def listen():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((listenip, int(port)))
        s.listen(1)
    except Exception,e:
        handle_exception()
        os._exit(1)
    s.setblocking(1)
    teller = 0
    while(1):
        time.sleep(0.1)
        try:
            insocket, addr = s.accept()
        except Exception, ex:
            handle_exception()
            os._exit(1)
        thread.start_new_thread(serve, (insocket, ))
        teller += 1
        thread.start_new_thread(dodcctest, ('test' + str(teller), \
insocket, nrloops))


def serve(insocket):
    global commandsdone
    f = insocket.makefile()
    while(1):
        try:
            r = f.readline()
            if not r:
                break
            rlog(100, 'DCC', r.strip())
            commandsdone += 1
        except Exception, ex:
            handle_exception()
            return

donot = ['reboot', 'cycle', 'loglevel', 'quit', 'email', 'meet', 'nick', \
'part', 'cc', 'chat', 'join', ' nick', 'update', 'install', \
'reconnect', 'jump', 'nonfree', 'relay', 'rss', 'fleet', 'sendraw', \
'upgrade', 'alarm', 'remind', 'intro', 'host', 'ip', 'alarm', 'tests', \
'unload', 'delete', 'dfwiki', 'dig', 'silent', 'reconnect', 'switch', 'op',
'dict', 'slashdot', 'films', 'latest', 'weather', 'coll', 'web', 'mail', \
'markov', 'probe', 'sc', 'log', 'validate']

def dodcctest(name, insocket, nrloop):
    a = examples.getexamples()
    teller = 0
    while 1:
        nrloop -= 1
        if nrloop == 0:
            break
        random.shuffle(a)
        for z in a:
            teller += 1
            no = 0
            for zz in donot:
                if z.find(zz) != -1:
                    no = 1
                    break
            if no:
                continue
            rlog(100, '%s %s-%s' % (name, nrloop, teller), 'sending ' \
+ str(z))
            insocket.send('!' + str(z) + ' chan ' + channel + '\n')
        teller = 0

thread.start_new_thread(listen, ())

def startirc(nr):
    testnick = mynick + str(nr)
    #i = gozerbot.bot.Bot('test@test', 'test')
    i = gozerbot.irc.Irc()
    try:
        i.connect(testnick, server, 6667)
    except:
        return
    ipip2 = socket.inet_aton(listenip)
    ipip = struct.unpack('>L', ipip2)[0]
    zz = 'DCC CHAT CHAT %s %s' % (ipip, port)
    i.ctcp(botnick, zz)

for i in range(nrbots):
    thread.start_new_thread(startirc, (i, ))
    time.sleep(timetosleep)

while(1):
    try:
        time.sleep(1)
    except:
        stop(0,0)
