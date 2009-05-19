# plugs/alarm.py
#
#

""" the alarm plugin allows for alarms that message the user giving the
 command at a certain time or number of seconds from now
"""

__copyright__ = 'this file is in the public domain'
__depending__ = ['todo', ]

from gozerbot.generic import handle_exception, rlog, strtotime, striptime, \
jsonstring
from gozerbot.utils.lazydict import LazyDict
from gozerbot.persist.persist import Persist
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.utils.nextid import nextid
from gozerbot.fleet import fleet
from gozerbot.datadir import datadir
from gozerbot.plughelp import plughelp
from gozerbot.aliases import aliases
from gozerbot.periodical import periodical
from gozerbot.tests import tests
import time, os, shutil

plughelp.add('alarm', 'remind the user with given txt at a certain time')

## UPGRADE PART

def upgrade():
    pass

## END UPGRARE PART

class Alarmitem(LazyDict):

    """ item holding alarm data """

    def __init__(self, botname='default', i=0, nick="", ttime=time.time(), txt="", \
printto=None, d={}):
        if not d:
            LazyDict.__init__(self)
            self.botname = botname
            self.idnr = i
            self.nick = nick
            self.time = ttime
            self.txt = txt
            self.printto = printto or ""
        else:
            LazyDict.__init__(self, d)

    def __str__(self):
        result = "%s %s %s %s %s" % (self.botname, self.idnr, self.nick, \
self.time, self.txt)
        return result

class Alarms(Persist):

    """ class that holds the alarms """

    def __init__(self, fname):
        Persist.__init__(self, fname)
        if not self.data:
            self.data = []
        for i in self.data:
            z = Alarmitem(d=i)
            try:
                getattr(z, 'printto')
            except AttributeError:
                setattr(z, 'printto', "")
            periodical.addjob(z.time - time.time(), 1, self.alarmsay, z.nick, \
z)

    def size(self):
        """ return number of alarms """
        return len(self.data)

    def bynick(self, nick):
        """ get alarms by nick """
        nick = nick.lower()
        result = []
        for i in self.data:
            z = Alarmitem(d=i)
            if z.nick == nick:
                result.append(z)
        return result

    def alarmsay(self, item):
        """ say alarm txt """
        bot = fleet.byname(item.botname)
        if bot:
            if item.printto:
                bot.say(item.printto, "[%s] %s" % (item.nick, item.txt), \
speed=1)
            else:
                bot.say(item.nick, item.txt, speed=1)
        self.delete(item.idnr)

    def add(self, botname, nick, ttime, txt, printto=None):
        """ add alarm """
        nick = nick.lower()
        nrid = nextid.next('alarms')
        item = Alarmitem(botname, nrid, nick, ttime, txt, printto=printto)
        pid = periodical.addjob(ttime - time.time(), 1, self.alarmsay, nick, \
item)
        item.idnr = pid
        self.data.append(item)
        self.save()
        return pid

    def delete(self, idnr):
        """ delete alarmnr """
        for i in range(len(self.data)-1, -1, -1):
            if Alarmitem(d=self.data[i]).idnr == idnr:
                del self.data[i]
                periodical.killjob(idnr)
                self.save()
                return 1

alarms = Alarms(datadir + os.sep + 'plugs' + os.sep + 'alarm' + os.sep + 'alarms')
if not alarms.data:
    alarms = Alarms(datadir + os.sep + 'plugs' + os.sep + 'alarm' + os.sep + 'alarms')
   
def shutdown():
    periodical.kill()

def size():
    """ return number of alarms """
    return alarms.size()

def handle_alarmadd(bot, ievent):
    """ alarm <txt-with-time> | <+delta> <txt> .. add an alarm """
    #if ievent.cmnd == 'DCC':
    #    ievent.reply("sorry can't run alarm from dcc chat")
    #    return 
    if not ievent.rest:
        ievent.reply('alarm <txt-with-time> or alarm <+delta> <txt>')
        return
    else:
        alarmtxt = ievent.rest
    # see if alarm time is given as delta aka starts with +
    if alarmtxt[0] == '+':
        try:
            sec = int(ievent.args[0][1:]) # get nr of seconds to sleep
        except ValueError:
            ievent.reply('use +nrofsecondstosleep')
            return
        if len(ievent.args) < 2:
            ievent.reply('i need txt to remind you')
            return
        try:
            ttime = time.time() + sec
            # check for time overflow
            if ttime > 2**31:
                ievent.reply("time overflow")
                return
            # add alarm 
            nrid = alarms.add(bot.name, ievent.nick, ttime, \
' '.join(ievent.args[1:]), ievent.printto)
            ievent.reply("alarm %s set at %s" % (nrid, time.ctime(ttime)))
            return
        except Exception, ex:
            handle_exception(ievent)
            return
    # see if we can determine time from txt
    alarmtime = strtotime(alarmtxt)
    if not alarmtime:
        ievent.reply("can't detect time")
        return
    # check if alarm txt is provided
    txt = striptime(alarmtxt).strip()
    if not txt:
        ievent.reply('i need txt to remind you')
        return
    if time.time() > alarmtime:
        ievent.reply("we are already past %s" % time.ctime(alarmtime))
        return
    # add alarm
    nrid = alarms.add(bot.name, ievent.nick, alarmtime, txt, ievent.printto)
    ievent.reply("alarm %s set at %s" % (nrid, time.ctime(alarmtime)))

cmnds.add('alarm', handle_alarmadd, 'USER', allowqueue=False)
examples.add('alarm', 'say txt at a specific time or time diff', \
'1) alarm 12:00 lunchtime 2) alarm 3-11-2008 0:01 birthday ! 3) alarm +180 \
egg ready')
tests.add('alarm 23:59 sleeptime', 'alarm (\d+) set at').add('alarm-del %s')

def handle_alarmlist(bot, ievent):
    """ alarm-list .. list all alarms """
    result = []
    for alarmdata in alarms.data:
        i = Alarmitem(d=alarmdata)
        result.append("%s) %s: %s - %s " % (i.idnr, i.nick, \
time.ctime(i.time), i.txt))
    if result:
        ievent.reply("alarmlist: ", result, dot=True)
    else:
        ievent.reply('no alarms')

cmnds.add('alarm-list', handle_alarmlist, 'OPER')
examples.add('alarm-list', 'list current alarms', 'alarm-list')
tests.add('alarm 23:59 sleeptime', 'alarm (\d+) set at').add('alarm-list', 'sleeptime').add('alarm-del %s')

def handle_myalarmslist(bot, ievent):
    """ alarm-mylist .. show alarms of user giving the command """
    result = []
    nick = ievent.nick.lower()
    for alarmdata in alarms.data:
        i = Alarmitem(d=alarmdata)
        if i.nick == nick:
            result.append("%s) %s - %s " % (i.idnr, time.ctime(i.time), i.txt))
    if result:
        ievent.reply("your alarms: ", result, dot=True)
    else:
        ievent.reply('no alarms')

cmnds.add('alarm-mylist', handle_myalarmslist, 'USER')
examples.add('alarm-mylist', 'list alarms of user giving the commands', \
'alarm-mylist')
aliases.data['myalarms'] = 'alarm-mylist'
tests.add('alarm 23:59 sleeptime', 'alarm (\d+) set at').add('alarm-mylist', 'sleeptime').add('alarm-del %s')

def handle_alarmdel(bot, ievent):
    """ alarm-del <nr> .. delete alarm """
    try:
        alarmnr = int(ievent.args[0])
    except IndexError:
        ievent.missing('<nr>')
        return
    except ValueError:
        ievent.reply('argument needs to be an integer')
        return
    if alarms.delete(alarmnr):
        ievent.reply('alarm with id %s deleted' % alarmnr)
    else:
        ievent.reply('failed to delete alarm with id %s' % alarmnr)

cmnds.add('alarm-del', handle_alarmdel, 'OPER')
examples.add('alarm-del', 'delete alarm with id <nr>', 'alarm-del 7')

