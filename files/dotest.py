#!/usr/bin/env python
#
# move this file to the bot directory

__copyright__ = 'this file is in the public domain'

from gozerbot.users import users
from gozerbot.config import config
from gozerbot.generic import handle_exception, enable_logging
import gozerbot.exit
import unittest, glob, signal, os, sys

nettests = ['collective', 'dig', 'dns', 'fleet', 'install', 'irc', 'jabber', \
'jcoll', 'nickcapture', 'probe', 'relay', 'rss', 'udp', 'update', 'upgrade', \
'webserver', 'wikipedia']

config['loglevel'] = 100
enable_logging()

sys.path.insert(0, os.getcwd())

# stop function
def stop(x, y):
    os._exit(0)

# register SIGTERM handler to stop
signal.signal(signal.SIGTERM, stop)

try:
    users.add('test', ['test@test', ], ['OPER', 'USER', 'QUOTE'])
except Exception, ex:
    pass

what = None
try:
    what = sys.argv[1]
except IndexError:
    pass

try:
    if what:
        if what == 'net':
            names =  map(lambda a: a[:-3], glob.glob('tests/*.py'))
            tmp = []
            for i in names:
                 for j in nettests:
                     if j in i:
                         tmp.append(i)
            names = tmp
        else:
            names = ['tests/%s' % what, ]
        suite = unittest.defaultTestLoader.loadTestsFromNames(names)
        unittest.TextTestRunner(verbosity=5).run(suite)
    else:
        names =  map(lambda a: a[:-3], glob.glob('tests/*.py'))
        tmp = []
        for i in names:
            got = 1
            for j in nettests:
                 if j in i:
                     got = 0
            if got:
                tmp.append(i)
        names = tmp
        suite = unittest.defaultTestLoader.loadTestsFromNames(names)
        unittest.TextTestRunner(verbosity=5).run(suite)
except KeyboardInterrupt:
    os._exit(0)
except Exception, ex:
    handle_exception()
os._exit(0)
