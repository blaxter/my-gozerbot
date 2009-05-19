# gozerbot/thr.py
#
#

""" own threading wrapper """

__copyright__ = 'this file is in the public domain'

from gozerbot.stats import stats
from gozerbot.generic import handle_exception, rlog, lockdec
import threading, re, time, thread

dontshowthreads = ['Periodical.runjob', ]

# regular expression to determine thread name
methodre = re.compile('method\s+(\S+)', re.I)
funcre = re.compile('function\s+(\S+)', re.I)

threadlock = thread.allocate_lock()
locked = lockdec(threadlock)

class Botcommand(threading.Thread):

    """ thread for running bot commands .. give feedback of exceptions to
        ircevent argument (second after bot) """

    def __init__(self, group, target, name, args, kwargs):
        threading.Thread.__init__(self, None, target, name, args, kwargs)
        self.name = name
        self.ievent = args[1]
        self.setDaemon(True)

    def run(self):
        """ run the bot command """
        try:
            rlog(10, 'thr', 'running bot command thread %s' % self.name) 
            stats.up('threads', self.name)
            result = threading.Thread.run(self)
            if self.ievent.closequeue:
                rlog(4, 'thr', 'closing queue for %s' % self.ievent.userhost)
                for i in self.ievent.queues:
                    i.put_nowait(None)
        except Exception, ex:
            handle_exception(self.ievent)
            time.sleep(0.1)

class Thr(threading.Thread):

    """ thread wrapper """

    def __init__(self, group, target, name, args, kwargs):
        threading.Thread.__init__(self, None, target, name, args, kwargs)
        rlog(-14, 'thr', 'running %s .. args: %s' % (name, args))
        self.setDaemon(True)
        self.name = name

    def run(self):
        """ run the thread """
        try:
            if self.name not in dontshowthreads:
                rlog(-4, 'thr', 'running thread %s' % self.name) 
            stats.up('threads', self.name)
            threading.Thread.run(self)
        except Exception, ex:
            handle_exception()
            time.sleep(0.1)

def getname(func):
    """ get name of function/method """
    name = ""
    method = re.search(methodre, str(func))
    if method:
        name = method.group(1)
    else: 
        function = re.search(funcre, str(func))
        if function:
            name = function.group(1)
        else:
            name = str(func)
    return name

def start_new_thread(func, arglist, kwargs=None):
    """ start a new thread .. set name to function/method name"""
    if not kwargs:
        kwargs = {}
    try:
        name = getname(func)
        if not name:
            name = 'noname'
        thread = Thr(None, target=func, name=name, args=arglist, \
kwargs=kwargs)
        rlog(-15, 'thr', 'starting %s thread' % str(func))
        thread.start()
        return thread
    except:
        handle_exception()
        time.sleep(0.1)

@locked
def start_bot_command(func, arglist, kwargs={}):
    """ start a new thread .. set name to function/method name"""
    if not kwargs:
        kwargs = {}
    try:
        name = getname(func)
        if not name:
            name = 'noname'
        thread = Botcommand(group=None, target=func, name=name, args=arglist, \
kwargs=kwargs)
        rlog(-15, 'thr', 'starting %s thread' % str(func))
        thread.start()
        return thread
    except:
        handle_exception()
        time.sleep(0.1)

def threaded(func):
    def threadedfunc(*args, **kwargs):
        start_new_thread(func, args, kwargs)
    return threadedfunc
