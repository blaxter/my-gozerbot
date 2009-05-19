# gozerbot/exit.py
#
#

""" gozerbot's finaliser """

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from generic import rlog
from eventhandler import mainhandler
from plugins import plugins
from fleet import fleet
from persist.persist import saving
from runner import runners_stop

# basic imports
import atexit, os, time

def globalshutdown():

    """ shutdown the bot. """

    rlog(10, 'GOZERBOT', 'SHUTTING DOWN')

    try:
        os.remove('gozerbot.pid')
    except:
        pass

    try:
        runners_stop()
        rlog(10, 'gozerbot', 'shutting down fleet')
        fleet.exit()
        rlog(10, 'gozerbot', 'shutting down plugins')
        plugins.exit()
        rlog(10, 'GOZERBOT', 'done')
        os._exit(0)
    except Exception, ex:
        rlog(10, 'gozerbot.exit', 'exit error %s:' % str(ex))

# register shutdown function
atexit.register(globalshutdown)
