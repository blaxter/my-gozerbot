# gozerbot/monitor.py
#
#

""" monitors .. call callback on bot output. """

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from gozerbot.stats import stats
from generic import rlog, handle_exception, calledfrom
from irc.ircevent import Ircevent
from config import config
from threads.threadloop import ThreadLoop
from runner import cbrunners
import threads.thr as thr

# basic imports
import Queue, sys

# try to import jabber stuff
try:
    from jabber.jabbermsg import Jabbermsg
    from jabber.jabberpresence import Jabberpresence
except ImportError, ex:
    rlog(10, 'monitor', str(ex))

class Monitor(ThreadLoop):

    """ monitor base class. """

    def __init__(self, name="monitor"):
        ThreadLoop.__init__(self, name)        
        self.outs = []

    def add(self, name, callback, pre, threaded=False):

        """ add a monitoring callback. """

        name = calledfrom(sys._getframe(0))

        if config['loadlist'] and name not in config['loadlist']:
            return

        self.outs.append((name, callback, pre, threaded))
        rlog(0, self.name, 'added %s (%s)' % (name, str(callback)))

    def unload(self, name):

        """ delete monitor callback. """

        name = name.lower()

        for i in range(len(self.outs)-1, -1, -1):
            if self.outs[i][0] == name:
                del self.outs[i]

    def handle(self, *args, **kwargs):

        """ fire monitor callbacks. """

        for i in self.outs:

            # check if precondition is met
            try:
                if i[2]:
                    stats.up('monitors', thr.getname(str(i[2])))
                    rlog(-10, 'jabbermonitor', 'checking inloop %s' % str(i[2]))
                    doit = i[2](*args, **kwargs)
                else:
                    doit = 1
            except Exception, ex:
                handle_exception()
                doit = 0

            if doit:
                # run monitor callback in its own thread
                rlog(0, 'jabbermonitor', 'excecuting jabbermonitor callback \
%s' % i[0])
                stats.up('monitors', thr.getname(str(i[1])))
                if not i[3]:
                    cbrunners[5].put("monitor-%s" % i[0], i[1], *args)
                else:
                    thr.start_new_thread(i[1], args, kwargs)

class Outmonitor(Monitor):

    """ monitor for bot output (bot.send). """

    def handle(self, bot, txt):

        """ fire outmonitor callbacks. """

        ievent = Ircevent().parse(bot, txt)

        if not ievent:
            rlog(10, 'monitor', "can't make ircevent: %s" % txt)
            return

        ievent.nick = bot.nick

        try:
            ievent.userhost = bot.userhosts[bot.nick]
        except KeyError:
            ievent.userhost = "bot@bot"

        Monitor.handle(self, bot, ievent)

class Jabbermonitor(Monitor):

    """ monitor jabber output """

    def handle(self, bot, event):

        """ fire jabber monitor callbacks. """

        msg = unicode(event)

        try:
            if msg.startswith('<presence'):
                jmsg = Jabberpresence(msg)
            else:
                jmsg = Jabbermsg(msg)
            jmsg.toirc(bot)
            jmsg.botoutput = True
            Monitor.handle(self, bot, jmsg)
        except AttributeError:
            if config['debug']:
                handle_exception()
            return

# bot.send() monitor
outmonitor = Outmonitor('outmonitor') 

# bot.say() monitor
saymonitor = Monitor('saymonitor')

# jabber monitor
jabbermonitor = Jabbermonitor('jabbermonitor')
