#!/usr/bin/env python
#
#

from gozerbot.generic import geturl
from gozerbot.examples import examples
from gozerbot.plugins import plugins
from gozerbot.thr import start_new_thread
import random, os, time

plugins.regplugins()

donot = ['reboot', 'cycle', 'loglevel', 'quit', 'email', 'meet', 'nick', \
'part', 'cc', 'chat', 'join', ' nick', 'update', 'install', \
'reconnect', 'jump', 'nonfree', 'relay', 'rss', 'fleet', 'sendraw', \
'upgrade', 'alarm', 'remind', 'intro', 'host', 'ip', 'alarm', 'tests', \
'unload', 'delete', 'dfwiki', 'dig', 'silent', 'reconnect', 'switch', 'op',
'dict', 'slashdot', 'films', 'latest', 'weather', 'coll', 'web', 'mail', \
'markov', 'probe', 'sc']

def dowebtest(nrloop):
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
            print z
            try:
                print geturl('http://localhost:8088/dispatch?command=%s' % z)
            except IOError:
                pass
            except:
                os._exit(0)            

for i in range(100):
    start_new_thread(dowebtest, (10, ))

try:
    while 1:
        time.sleep(1)
except:
    os._exit(0)
