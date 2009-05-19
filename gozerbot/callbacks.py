# gozerbot/callbacks.py
#
#

""" bot callbacks .. seperate classes for IRC and Jabber."""

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from gozerbot.stats import stats
from gozerbot.threads.thr import getname 
from config import config
from generic import rlog, handle_exception, calledfrom, makeargrest, lockdec
from utils.dol import Dol
from threads.thr import start_new_thread, getname
from runner import cbrunners

# basic imports
import sys, copy, thread

# locks
callbacklock = thread.allocate_lock()
locked = lockdec(callbacklock)

class Callback(object):

    """ class representing a callback. """

    def __init__(self, func, prereq, plugname, kwargs, threaded=False, \
speed=5):
        self.func = func # the callback function
        self.prereq = prereq # pre condition function
        self.plugname = plugname # plugin name
        self.kwargs = kwargs # kwargs to pass on to function
        self.threaded = copy.deepcopy(threaded) # run callback in thread
        self.speed = copy.deepcopy(speed) # speed to execute callback with
        stats.up('callbacks', 'created')

class Callbacks(object):

    """ dict of lists containing callbacks. """

    def __init__(self):

        # cbs are the callbacks .. 1 list per ievent.CMND
        self.cbs = Dol()

    def size(self):

        """ return number of callbacks. """

        return len(self.cbs)

    @locked
    def add(self, what, func, prereq=None, kwargs=None, threaded=False, nr=False, speed=5):

        """ add a callback. """

        what = what.upper()

        # get the plugin this callback was registered from
        plugname = calledfrom(sys._getframe(1))

        # check if plugname is in loadlist .. if not don't add callback
        if config['loadlist'] and not plugname in config['loadlist']:
            return

        # see if kwargs is set if not init to {}
        if not kwargs:
            kwargs = {}

        # add callback to the dict of lists
        if nr != False:
            self.cbs.insert(nr, what, Callback(func, prereq, plugname, kwargs, threaded, speed))
        else:
            self.cbs.add(what, Callback(func, prereq, plugname, kwargs, threaded, speed))

        rlog(-3, 'callbacks', 'added %s (%s)' % (what, plugname))

    def unload(self, plugname):

        """ unload all callbacks registered in a plugin. """

        unload = []

        # look for all callbacks in a plugin
        for name, cblist in self.cbs.iteritems():
            index = 0
            for item in cblist:
                if item.plugname == plugname:
                    unload.append((name, index))
                index += 1

        # delete callbacks
        for callback in unload[::-1]:
            self.cbs.delete(callback[0], callback[1])
            rlog(1, 'callbacks', 'unloaded %s' % callback[0])

    def whereis(self, cmnd):

        """ show where ircevent.CMND callbacks are registered """

        result = []
        cmnd = cmnd.upper()

        # locate callbacks for CMND
        for c, callback in self.cbs.iteritems():
            if c == cmnd:
                for item in callback:
                    if not item.plugname in result:
                        result.append(item.plugname)

        return result

    def list(self):

        """ show all callbacks. """

        result = []

        # loop over callbacks and collect callback functions
        for cmnd, callbacks in self.cbs.iteritems():
            for cb in callbacks:
                result.append(getname(cb.func))

        return result

    def check(self, bot, ievent):

        """ check for callbacks to be fired. """

        # check for "ALL" callbacks
        if self.cbs.has_key('ALL'):
            for cb in self.cbs['ALL']:
                stats.up('callbacks', 'ALL')
                self.callback(cb, bot, ievent)

        cmnd = ievent.cmnd.upper()

        # check for CMND callbacks
        if self.cbs.has_key(cmnd):
            for cb in self.cbs[cmnd]:
                stats.up('callbacks', cmnd)
                self.callback(cb, bot, ievent)

    @locked    
    def callback(self, cb, bot, ievent):

        """ callback cb with bot and ievent as arguments """

        try:

            # see if the callback pre requirement succeeds
            if cb.prereq:
                rlog(-10, 'callback', 'excecuting in loop %s' % str(cb.prereq))
                if not cb.prereq(bot, ievent):
                    return

            # check if callback function is there
            if not cb.func:
                return

            # log and stats
            rlog(0, 'callback', 'excecuting callback %s' % str(cb.func))
            stats.up('callbacks', getname(cb.func))
            stats.up('callbacks', cb.plugname)

            # launcn the callback .. either threaded or dispatched at runners
            if cb.threaded:
                start_new_thread(cb.func, (bot, ievent), cb.kwargs)
            else:
                cbrunners[10-cb.speed].put("cb-%s" % cb.plugname, cb.func, bot, ievent, **cb.kwargs)

        except Exception, ex:
            handle_exception()

# callbacks object is the same for ICR and Jabber
callbacks = jcallbacks = Callbacks()
