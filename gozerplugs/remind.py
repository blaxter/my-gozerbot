# plugs/remind.py
#
#

""" remind people .. say txt when somebody gets active """

__copyright__ = 'this file is in the public domain'

from gozerbot.utils.generic import convertpickle
from gozerbot.generic import getwho, lockdec
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.callbacks import callbacks, jcallbacks
from gozerbot.datadir import datadir
from gozerbot.persist.pdol import Pdol
from gozerbot.plughelp import plughelp
import time, os, thread

plughelp.add('remind', 'check if user says something if so do /msg')

## UPGRADE PART

def upgrade():
    try:
        convertpickle(datadir + os.sep + 'remind', datadir + os.sep + 'plugs' + \
os.sep + 'remind' + os.sep + 'remind')
    except:
        pass

## END UPGRADE PART

remindlock = thread.allocate_lock()
rlocked = lockdec(remindlock)

class Remind(Pdol):

    """ remind object """

    def __init__(self, name):
        Pdol.__init__(self, name)

    @rlocked
    def add(self, who, data):
        """ add a remind txt """
        self[who] = data
        self.save()

    def wouldremind(self, userhost):
        """ check if there is a remind for userhost """
        reminds = self[userhost]
        if reminds == None or reminds == []:
            return 0
        return 1

    @rlocked
    def remind(self, bot, userhost):
        """ send a user all registered reminds """
        reminds = self[userhost]
        if not reminds:
            return
        for i in reminds:
            ttime = None
            try:
                (tonick, fromnick, txt, ttime) = i
            except ValueError:
                (tonick, fromnick, txt) = i
            txtformat = '[%s] %s wants to remind you of: %s'
            if ttime:
                timestr = time.ctime(ttime)
            else:
                timestr = None
            if bot.jabber:
                bot.saynocb(userhost, txtformat % (timestr, fromnick, txt), \
fromm=tonick, groupchat=False)
                bot.saynocb(fromnick, '[%s] reminded %s of: %s' % (timestr, \
tonick, txt))
            else:
                bot.say(tonick, txtformat % (timestr, fromnick, txt), \
fromm=tonick, speed=1)
                bot.say(fromnick, '[%s] reminded %s of:  %s' % (timestr, \
tonick, txt), speed=1)
        del self[userhost]
        self.save()

remind = Remind(datadir + os.sep + 'plugs' + os.sep + 'remind' + os.sep + \
'remind')
if not remind.data:
    remind = Remind(datadir + os.sep + 'plugs' + os.sep + 'remind' + os.sep + \
'remind')

def preremind(bot, ievent):
    """ remind precondition """
    return remind.wouldremind(ievent.userhost)

def remindcb(bot, ievent):
    """ remind callbacks """
    remind.remind(bot, ievent.userhost)

# monitor privmsg and joins
callbacks.add('PRIVMSG', remindcb, preremind, threaded=True)
callbacks.add('JOIN', remindcb, preremind, threaded=True)
jcallbacks.add('Message', remindcb, preremind, threaded=True)

def handle_remind(bot, ievent):
    """ remind <nick> <txt> .. add a remind """
    try:
        who = ievent.args[0]
        txt = ' '.join(ievent.args[1:])
    except IndexError:
        ievent.missing('<nick> <txt>')
        return
    if not txt:
        ievent.missing('<nick> <txt>')
        return
    userhost = getwho(bot, who)
    if not userhost:
        ievent.reply("can't find userhost for %s" % who)
        return
    else:
        if ievent.jabber:
            remind.add(userhost, (who, ievent.userhost, txt, time.time()))
        else:
            remind.add(userhost, (who, ievent.nick, txt, time.time()))
        ievent.reply("remind for %s added" % who)

cmnds.add('remind', handle_remind, 'USER', allowqueue=False)
examples.add('remind', 'remind <nick> <txt>', 'remind dunker check the bot !')
