# plugs/log.py
#
#

""" logging """

__copyright__ = 'this file is in the public domain'
__gendocfirst__ = ['log-on', ]
__gendoclast__ = ['log-off', ]
__depending__ = ['mail' , 'markov']

from gozerbot.generic import rlog, handle_exception, elapsedstring, dmy, \
hourmin, lockdec, strtotime
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.callbacks import callbacks, jcallbacks
from gozerbot.plughelp import plughelp
from gozerbot.monitor import saymonitor, jabbermonitor
from gozerbot.aliases import aliases, aliasdel
from gozerbot.users import users
import glob, re, thread, pickle, os, mmap, time

plughelp.add('log', 'logs related commands')

# check if logs dir exists if not create it
if not os.path.isdir('logs'):
    os.mkdir('logs')

loglock = thread.allocate_lock()
locked = lockdec(loglock)

class Logs(object):

    """ hold handles to log files (per channel) """

    def __init__(self, logdir):
        self.logdir = logdir
        self.maps = {}
        self.files = {}
        self.filenames = {}
        self.lock = thread.allocate_lock()
        self.loglist = []
        try:
            loglistfile = open(self.logdir + os.sep + 'loglist', 'r')
            self.loglist = pickle.load(loglistfile)
        except:
            self.loglist = []
        rlog(0, 'logs', 'loglist is %s' % str(self.loglist))
        # open log files in append mode
        for i in glob.glob(self.logdir + os.sep + '*.log'):
            reresult = re.search('logs%s(.+)\.' % os.sep, i)
            filename = reresult.group(1)
            if not filename:
                rlog(10, 'logs', "can't determine channel name")
                continue
            logfile = open(i, 'a')
            if logfile:
                self.files[filename] = logfile
                self.filenames[filename.lower()] = i
                rlog(1, 'logs', 'adding file %s' % i)
            else:
                rlog(10, 'logs', 'failed to open %s' % i)

    def save(self):
        """ save loglist """
        try:
            self.lock.acquire()
            picklefile = open(self.logdir + os.sep + 'loglist', 'w')
            pickle.dump(self.loglist, picklefile)
            rlog(0, 'logs', 'loglist saved')
        finally:
            self.lock.release()

    def close(self):
        """ close log files """
        try:
            self.lock.acquire()
            for i in self.files.keys():
                rlog(10, 'logs', 'closing ' + str(i))
                self.files[i].close()
        finally:
            self.lock.release()
        self.save()

    def size(self, channel):
        """ get size of log file """
        if channel[0] in ['#', '!', '&', '+']:
            chan = channel[1:].lower()
        else:
            chan = channel.lower()
        try:
            size = os.stat(self.filenames[chan])[6]
            return size
        except (IOError, KeyError):
            return 0

    def add(self, channel):
        """ add logfile for channel """
        if channel[0] in ['#', '!', '&', '+']:
            chan = channel[1:].lower()
        else:
            chan = channel.lower()
        filename = self.logdir + os.sep + chan + '.log'
        rlog(10, 'logs', 'adding logfile %s' % chan)
        if self.files.has_key(chan):
            rlog(10, 'logs', 'already opened file %s' % chan)
            return 1
        try:
            logfile = open(filename,'a')
            self.files[chan] = logfile
            self.filenames[chan] = filename
            if channel not in self.loglist:
                self.loglist.append(channel)
            return 1
        except Exception, ex:
            handle_exception()
            return 0

    def logbot(self, name, ttime, channel, txt):
        """ log stuff spoken by the bot """
        if channel not in self.loglist:
            rlog(1, 'logs', "%s not in loglist" % channel)
            return
        if channel[0] in ['#', '!', '&', '+']:
            chan = channel[1:].lower()
        else:
            chan = channel.lower()
        filename = self.logdir + os.sep + chan + '.log'
        if not self.files.has_key(chan):
            if not self.add(channel):
                rlog(1, 'logs', "can't create logfile %s" % filename)
                return
        logfile = self.files[chan]
        logitem = (name, ttime, 'bot', 'bot@bot', txt)
        rlog(-1, 'logs', 'logging [%s] <%s> %s ==> %s' % (name, 'bot', txt, \
filename))
        # write the data to file (comma seperated)
        try:
            self.lock.acquire()
            logfile.write('%s,%s,%s,%s,%s\n' % logitem)
            logfile.flush()
        finally:
            self.lock.release()

    def log(self, name, ttime, ievent):
        """ log ircevent """
        if ievent.nick == ievent.bot.nick:
            ievent.nick = 'bot'
            ievent.userhost = 'bot@bot'
        channel = ievent.channel
        if channel not in self.loglist:
            rlog(1, 'logs', "%s not in loglist" % channel)
            return
        if channel[0] in ['#', '!', '&', '+']:
            chan = channel[1:].lower()
        else:
            chan = channel.lower()
        filename = self.logdir + os.sep + chan + '.log'
        if not self.files.has_key(chan):
            if not self.add(ievent.channel):
                rlog(1, 'logs', "can't create logfile %s" % filename)
                return
        # put ievent.cmnd as first txt
        if ievent.cmnd == 'PRIVMSG' or ievent.cmnd == 'Message':
            if ievent.usercmnd:
                tmp = "CMND: " + ievent.txt
            else:
                if ievent.txt.startswith('\001ACTION'):
                    txt = ievent.txt[7:-1]
                    tmp = "PRIVMSG: /me " + txt
                else:
                    tmp = "PRIVMSG: " + ievent.txt
        elif ievent.cmnd == 'MODE':
            tmp = "MODE: " + ievent.postfix
        elif ievent.cmnd == 'PART':
            tmp = "PART: " + ievent.channel
        elif ievent.cmnd == 'JOIN':
            tmp = "JOIN: " + ievent.channel
        else:
            return
        logfile = self.files[chan]
        logitem = (name, ttime, ievent.nick, ievent.userhost, tmp)
        rlog(-1, 'logs', 'logging [%s] <%s> %s ==> %s' % (name, ievent.nick, \
ievent.txt, filename))
        # write the data to file (comma seperated)
        try:
            self.lock.acquire()
            logfile.write('%s,%s,%s,%s,%s\n' % logitem)
            logfile.flush()
        finally:
            self.lock.release()

    def getmmap(self, channel):
        """ get an mmap of a channel .. as of 0.8 this just returns the 
            open logfile
        """
        if not channel:
            return
        if channel[0] in ['#', '!', '&', '+']:
            chan = channel[1:].lower()
        else:
            chan = channel.lower()
        try:
            filename = self.filenames[chan]
        except KeyError:
            rlog(10, 'log', 'logging is not enabled in %s' % channel)
            return
        logfile = open(filename, 'r')
        #size = self.size(channel)
        #if size == 0:  
        #    return None
        #logmap = mmap.mmap(logfile.fileno(), size, mmap.MAP_SHARED, \
#access=mmap.ACCESS_READ)
        return logfile

    def loop(self, logmap, nrtimes, func, withbot=False, withcmnd=False):
        """ loop over the logmap """
        logmap.seek(0)
        teller = 0
        times = 0
        for line in logmap:
            teller += 1
            if teller % 100000 == 0:
                time.sleep(0.0001)
            try:
                (botname, ttime, nick, userhost, txt) = \
line.strip().split(',', 4)
            except ValueError:
                continue
            if not withbot and userhost == 'bot@bot':
                continue
            if not withcmnd and txt.startswith('CMND:'):
                continue
            try:
                res = func(botname, ttime, nick, userhost, txt)
            except ValueError:
                continue
            if res:
                times += 1
                if nrtimes and times > nrtimes:
                    break
        logmap.close()

    def search(self, channel, what, nrtimes):
        """ search through logfile """
        res = []
        if not channel:
            return res
        andre = re.compile(' and ', re.I)
        ands = re.split(andre, what)
        nrtimes = int(nrtimes)
        logmap = self.getmmap(channel)
        if not logmap:
            return res
        res = []
        def dofunc(botname, ttime, nick, userhost, txt):
            """ search log line for matching txt """
            for j in ands:
                if txt.find(j.strip()) == -1:
                    return
            res.append((botname, ttime, nick, userhost, txt))
            return 1
        self.loop(logmap, nrtimes, dofunc)        
        if res:
            return res[:nrtimes]

    def seen(self, channel, who):
        """ get last line of who """
        result = []
        logmap = self.getmmap(channel)
        if not logmap:
            return result
        who = who.lower()
        if '*' in who:
            who = who.replace('*', '.*')
            rewho = re.compile(who)
            def dofunc(botname, ttime, nick, userhost, txt):
                """ add line that matches mask """
                if re.match(rewho, nick.lower()):
                    result.append((botname, ttime, nick, userhost, txt))
        else:
            def dofunc(botname, ttime, nick, userhost, txt):
                """ add line that matches nick """
                if nick.lower() == who:
                    result.append((botname, ttime, nick, userhost, txt))
        self.loop(logmap, None, dofunc)
        if result:
            return result[-1]

    def back(self, channel, what, nrtimes):
        """ search through the logs backwards """
        res = []
        if not channel:
            return res
        andre = re.compile(' and ', re.I)
        ands = re.split(andre, what)
        nrtimes = int(nrtimes)
        logmap = self.getmmap(channel)
        if not logmap:
            return res
        def dofunc(botname, ttime, nick, userhost, txt):
            """ add line that matches """
            for j in ands:
                if txt.find(j.strip()) == -1:
                    return
            res.append((botname, ttime, nick, userhost, txt))
            return 1
        self.loop(logmap, None, dofunc)
        result = []
        if res:
            if len(res) > nrtimes:
                result = res[len(res)-nrtimes:]
            else:
                result = res
        result.reverse()
        return result

    def bback(self, channel, what, nrtimes):
        """ search through the bot logs backwards """
        res = []
        if not channel:
            return res
        andre = re.compile(' and ', re.I)
        ands = re.split(andre, what)
        nrtimes = int(nrtimes)
        logmap = self.getmmap(channel)
        if not logmap:
            return res
        def dofunc(botname, ttime, nick, userhost, txt):
            """ add line that matches """
            if nick != 'bot':
                return
            for j in ands:
                if txt.find(j.strip()) == -1:
                    return
            res.append((botname, ttime, nick, userhost, txt))
            return 1
        self.loop(logmap, None, dofunc, withbot=True)
        result = []
        if res:
            if len(res) > nrtimes:
                result = res[len(res)-nrtimes:]
            else:
                result = res
        result.reverse()
        return result

    def fromtime(self, channel, ftime):
        """ returns log items from a certain time """
        res = []
        if not channel:
            return res
        logmap = self.getmmap(channel)
        if not logmap:
            return res
        def dofunc(botname, ttime, nick, userhost, txt):
            """ add line that is older then given time """
            logtime = float(ttime)
            if logtime > ftime:
                res.append((botname, ttime, nick, userhost, txt))
        self.loop(logmap, None, dofunc)
        return res

    def fromtimewithbot(self, channel, ftime):
        """ returns log items from a certain time """
        res = []
        if not channel:
            return res
        logmap = self.getmmap(channel)
        if not logmap:
            return res
        def dofunc(botname, ttime, nick, userhost, txt):
            """ add line that is older then given time including bot outout """
            logtime = float(ttime)
            if logtime > ftime:
                res.append((botname, ttime, nick, userhost, txt))
        self.loop(logmap, None, dofunc, withbot=True)
        return res

    def linesback(self, channel, nrtimes):
        """ return nr log lines back """
        result = []
        if not channel:
            return result
        nrtimes = int(nrtimes)
        logmap = self.getmmap(channel)
        if not logmap:
            return result
        def dofunc(botname, ttime, nick, userhost, txt):
            """ add line """
            result.append((botname, ttime, nick, userhost, txt))
            return 1
        self.loop(logmap, None, dofunc)
        if len(result) > nrtimes:
            return result[len(result)-nrtimes:]
        else:
            return result

    def linesbacknick(self, channel, who, nrtimes):
        """ return log lines for nick """
        result = []
        if not channel:
            return result
        nrtimes = int(nrtimes)
        logmap = self.getmmap(channel)
        if not logmap:
            return result
        def dofunc(botname, ttime, nick, userhost, txt):
            """ add line said by nick """
            if nick.lower() == who.lower():
                result.insert(0, (botname, ttime, nick, userhost, txt))
                return 1
        self.loop(logmap, None, dofunc)
        return result[:nrtimes]

    def linesbacknicksearch(self, channel, who, searchitem, nrtimes):
        """ search logs for lines said by who """
        result = []
        if not channel:
            return result
        who = who.lower()
        andre = re.compile(' and ', re.I)
        ands = re.split(andre, searchitem)
        nrtimes = int(nrtimes)
        logmap = self.getmmap(channel)
        if not logmap:
            return result
        def dofunc(botname, ttime, nick, userhost, txt):
            """ add line that is said by nick containing txt """
            if nick.lower() == who.lower():
                got = 0
                for j in ands:
                    if txt.find(j.strip()) == -1:
                        got = 0
                        break
                    got = 1
                if got:
                    result.append((botname, ttime, nick, userhost, txt))
                    return 1
        self.loop(logmap, None, dofunc)
        if len(result) > nrtimes:
            return result[len(result)-nrtimes:]
        else:
            return result

    def lastspoke(self, channel, userhost):
        """ return time of last line spoken by user with userhost """
        result = []
        if not channel:
            return result
        logmap = self.getmmap(channel)
        if not logmap:
            return result
        def dofunc(botname, ttime, nick, uh, txt):
            """ add line that matches userhost """
            if userhost == uh:
                result.append(int(float(ttime)))
        self.loop(logmap, None, dofunc)
        return result[-1]

    def lastspokelist(self, channel, userhost, nrtimes):
        """ return time of last line spoken by user with userhost """
        result = []
        if not channel:
            return result
        logmap = self.getmmap(channel)
        if not logmap:
            return result
        def dofunc(botname, ttime, nick, uh, txt):
            """ add line that matches userhost """
            if userhost == uh:
                result.append(int(float(ttime)))
        self.loop(logmap, None, dofunc)
        return result[len(result)-nrtimes:]
         
    def lastnicks(self, channel, nrtimes):
        """ return the nicks of last said lines """
        result = []
        if not channel:
            return result
        logmap = self.getmmap(channel)
        if not logmap:
            return result
        def dofunc(botname, ttime, nick, userhost, txt):
            """ add nicks  """
            result.append(nick)
        self.loop(logmap, None, dofunc)
        if len(result) > nrtimes:
            result = result[len(result)-nrtimes:]
        result.reverse()
        return result

logs = Logs('logs')

def shutdown():
    logs.save()

def prelogsay(botname, printto, txt, who, how, fromm):
    """ determine if logsay callback needs to be called """
    if printto in logs.loglist:
        return 1

def cblogsay(botname, printto, txt, who, how, fromm):
    """ log the bots output """
    logs.logbot(botname, time.time(), printto, txt)

saymonitor.add('log', cblogsay, prelogsay)

def jprelogsay(botname, msg):
    """ jabber log precondition """
    try:
        to = str(msg.getTo())
    except:
        return
    if to in logs.loglist:
        return 1

def jcblogsay(botname, msg):
    """ log the jabber message """
    try:
        to = str(msg.getTo())
        txt = msg.getBody()
    except:
        return
    logs.logbot(botname, time.time(), to, txt)

jabbermonitor.add('log', jcblogsay, jprelogsay)

def prelog(bot, ievent):
    """ log pre condition """
    if ievent.channel and ievent.channel in logs.loglist:
        return 1

def logcb(bot, ievent):
    """ callback that logs ievent """
    logs.log(bot.name, time.time(), ievent)

callbacks.add('ALL', logcb, prelog)
jcallbacks.add('Message', logcb, prelog)

def handle_logon(bot, ievent):
    """ log-on .. enable logging in channel the command was given in """
    if not ievent.channel in logs.loglist:
        logs.loglist.append(ievent.channel)
        ievent.reply('logging enabled in %s' % ievent.channel)
    else:
        ievent.reply('%s already in loglist' % ievent.channel)

cmnds.add('log-on', handle_logon, 'OPER')
examples.add('log-on', 'enable logging of the channel in which the command \
was given', 'log-on')

def handle_logoff(bot, ievent):
    """ log-off .. disable logging in channel the command was given in"""
    try:
        logs.loglist.remove(ievent.channel)
        ievent.reply('logging disabled in %s' % ievent.channel)
    except ValueError:
        ievent.reply('%s not in loglist' % ievent.channel)

cmnds.add('log-off', handle_logoff, 'OPER')
examples.add('log-off', 'disable logging of the channel in which the command \
was given', 'log-off')

def handle_loglist(bot, ievent):
    """ log-list .. show list of channels that are being logged """
    ievent.reply(str(logs.loglist))

cmnds.add('log-list', handle_loglist, 'OPER')
examples.add('log-list', 'show list of current logged channels', 'log-list')

def handle_loglen(bot, ievent):
    """ log-len show length of logfile for channel in which command was \
        given """
    if ievent.channel not in logs.loglist:
        ievent.reply('logging not enabled in %s' % ievent.channel)
        return
    if ievent.channel[0] in ['#', '!', '&', '+']:
        chan = ievent.channel[1:].lower()
    else:
        chan = ievent.channel.lower()
    ievent.reply(str(logs.size(chan)))

cmnds.add('log-len', handle_loglen, 'OPER')
examples.add('log-len', 'show size of log file of the channel the command \
was given in', 'log-len')
aliases.data['log-size'] = 'log-len'

def sayresult(bot, ievent, result, withbot=False):
    """ reply with result """
    got = 0
    if result:
        res = []
        for i in result:
            try:
                if not withbot and i[3] == 'bot@bot':
                    continue
                if not withbot and ('PRIVMSG' in i[4] or 'CMND' in i[4]):
                    what = i[4].split(':', 1)[1].strip()
                else:
                    what = i[4].strip()
                res.append("[%s %s] <%s> %s" % (dmy(float(i[1])), \
hourmin(float(i[1])), i[2], what))
                got += 1
            except (ValueError, IndexError):
                rlog(10, 'log', "can't parse %s" % i)
        ievent.reply(res, dot=True)
    if not got:
        ievent.reply("nothing found")

def handle_logback(bot, ievent):
    """ log-back [<nrtimes>] <txt> .. search back through channel log """
    if not ievent.channel:
        ievent.reply("use chan <channelname> to set channel to search in")
        return
    if ievent.channel not in logs.loglist:
        ievent.reply('logging not enabled in %s' % ievent.channel)
        return
    try:
        nrtimes = int(ievent.args[0])
        txt = ' '.join(ievent.args[1:])
    except ValueError:
        txt = ievent.rest
        nrtimes = 100000
    except IndexError:
        ievent.missing('<searchitem> or <nrtimes> <searchitem>')
        return
    result = logs.back(ievent.channel, txt, nrtimes)
    sayresult(bot, ievent, result)

cmnds.add('log-back', handle_logback, ['USER', 'WEB', 'CLOUD'], speed=3)
examples.add('log-back', "log-back [<nrlinesback>] <txt> .. search backwards in log \
file of channel", '1) log-back http 2) log-back 1 http')
aliases.data['b'] = 'log-back'
aliases.data['back'] = 'log-back'

def handle_logbback(bot, ievent):
    """ log-botback [<nrtimes>] <txt> ['back' <bytesback>] .. search back \
        through bot output in the channel log """
    if not ievent.channel:
        ievent.reply("use chan <channelname> to set channel to search in")
        return
    if ievent.channel not in logs.loglist:
        ievent.reply('logging not enabled in %s' % ievent.channel)
        return
    try:
        nrtimes = int(ievent.args[0])
        txt = ' '.join(ievent.args[1:])
    except ValueError:
        txt = ievent.rest
        nrtimes = 100000
    except IndexError:
        ievent.missing('<searchitem> or <nrtimes> <searchitem>')
        return
    result = logs.bback(ievent.channel, txt, nrtimes)
    sayresult(bot, ievent, result, withbot=True)

cmnds.add('log-bback', handle_logbback, ['USER', 'WEB', 'CLOUD'], speed=3)
examples.add('bback', "log-bback [<nrtimes>] <txt> ['back' <bytesback>] .. \
search backwards in the bot output of the channel log file", '1) log-back \
http 2) log-back 1 http')
aliases.data['bback'] = 'log-bback'

def handle_logsearch(bot, ievent):
    """ log-search [<nrtimes>] <txt> ['back' <bytesback>] .. search the log \
        from the beginning """
    if not ievent.channel:
        ievent.reply("use chan <channelname> to set channel to search in")
        return
    if ievent.channel not in logs.loglist:
        ievent.reply('logging not enabled in %s' % ievent.channel)
        return
    try:
        nrtimes = int(ievent.args[0])
        txt = ' '.join(ievent.args[1:])
    except ValueError:
        txt = ievent.rest
        nrtimes = 100000
    except IndexError:
        ievent.missing(' <searchitem> or <nrtimes> <searchitem>')
        return
    result = logs.search(ievent.channel, txt, nrtimes)
    sayresult(bot, ievent, result)

cmnds.add('log-search', handle_logsearch, ['USER', 'WEB', 'CLOUD'], speed=3)
examples.add('log-search', 'log-search [<nrtimes>] <txt> .. search the log \
from the beginning', '1) log-search http 2) log-search 10 http')
aliasdel('search')

def handle_loglast(bot, ievent):
    """ log-last [<nr>] [<nick>] [<txt>] .. search log for last lines of
        <nick> containing <txt> """
    if ievent.channel not in logs.loglist:
        ievent.reply('logging not enabled in %s' % ievent.channel)
        return
    result = []
    try:
        nrlines = int(ievent.args[0])
        del ievent.args[0]
    except (IndexError, ValueError):
        nrlines = 100000
    try:
        nick, txt = ievent.args
    except ValueError:
        txt = None
        try:
            nick = ievent.args[0]
        except IndexError:
            nick = None
    if nick and txt:
        result = logs.linesbacknicksearch(ievent.channel, nick, txt, \
nrlines)
    elif nick: 
        result = logs.linesbacknick(ievent.channel, nick, nrlines)
    else:
        result = logs.linesback(ievent.channel, nrlines)
    if result:
        sayresult(bot, ievent, result)
    else:
        ievent.reply('no result found')

cmnds.add('log-last', handle_loglast, ['USER', 'WEB', 'CLOUD'], speed=3)
examples.add('log-last', 'log-last [<nr>] [<nick>] [<txt>] .. show lastlines \
of channel or user', '1) log-last dunker 2) log-last 5 dunker 3) log-last \
dunker http 4) log-last 5 dunker http')
aliases.data['last'] = 'log-last'

def handle_logtime(bot, ievent):
    """ show log from a certain time """
    if not logs:
        ievent.reply('log plugin is not enabled')
        return
    if ievent.channel not in logs.loglist:
        ievent.reply('logging is not enabled in %s' % ievent.channel)
        return
    fromtime = strtotime(ievent.rest)
    if not fromtime:
        ievent.reply("can't detect time")
        return
    result = logs.fromtimewithbot(ievent.channel, fromtime)
    if result:
        username = users.getname(ievent.userhost)
        res = []
        for i in result:
            if i[2] == 'bot':
                txt = i[4]
            else:
                nr = i[4].find(' ')
                txt = i[4][nr:].strip()
            res.append("[%s] <%s> %s" % (hourmin(float(i[1])), i[2], txt))
        ievent.reply(res)
        return
    ievent.reply('no data found')
    
cmnds.add('log-time', handle_logtime, ['USER', 'WEB', 'CLOUD'])
examples.add('log-time', 'show log since given time', 'log-time 21:00')

def handle_active(bot, ievent):
    """ active [<minback>] .. show who has been active, default is the 
        last 15 min 
    """
    if not logs:
        ievent.reply('log plugin is not enabled')
        return
    if ievent.channel not in logs.loglist:
        ievent.reply('logging is not enabled in %s' % ievent.channel)
        return
    try:
        channel = ievent.args[0].lower()
    except IndexError:
        channel = ievent.channel
    minback = 15
    result = [] 
    for i in logs.fromtime(ievent.channel, time.time() - 15*60):
        if i[2] not in result:
            result.append(i[2])
    if len(result) > 1:
        ievent.reply("active in the last %s minutes: " % minback, result)
    elif len(result) == 1:
        ievent.reply("%s is active" % result[0])
    else:
        ievent.reply("nobody active")

cmnds.add('active', handle_active, ['USER', 'WEB', 'CLOUD'])
examples.add('active', 'active [<minutesback>] .. show who has been active \
in the last 15 or <minutesback> minutes', '1) active 2) active 600')
aliases.data['a'] = 'active'

def handle_line(bot, ievent):
    """ line .. show activity of last hour """
    if not logs:
        ievent.reply('log plugin is not enabled')
        return
    if ievent.channel not in logs.loglist:
        ievent.reply('logging is not enabled in %s' % ievent.channel)
        return
    now = time.time()
    times = [0]*61
    for i in logs.fromtime(ievent.channel, time.time() - 60*60):
        try:
            diff = float(now - float(i[1]))
        except ValueError:
            continue
        times[int(diff/60)] += 1
    result = ""
    for j in range(61):
        if times[j]:
            result += "%s " % times[j]
        else:
            result += "- "
    result += '(number of lines per minute for the last hour .. \
most recent minute first)'
    ievent.reply(result) 

cmnds.add('line', handle_line, ['USER', 'WEB', 'CLOUD'])
examples.add('line', 'show activity for the last hour', 'line')
aliases.data['l'] = 'line'

# thnx to timp for this one
def handle_dayline(bot, ievent):
    """ dayline .. show activity for last 24 hours """
    if not logs:
        ievent.reply('log plugin is not enabled')
        return
    if ievent.channel not in logs.loglist:
        ievent.reply('logging is not enabled in %s' % ievent.channel)
        return
    now = time.time()
    times = [0]*25   
    for i in logs.fromtime(ievent.channel, time.time() - 24*60*60):
        diff = int(now/1440 - float(i[1])/1440)
        if diff < 25:
            times[diff] += 1
    result = ""
    for j in range(25):
        if times[j]:   
            result += "%s " % times[j]
        else:
            result += "- "
    result += ' (nr lines per hour for the last day .. most recent hour first)'
    ievent.reply(result)

cmnds.add('dayline', handle_dayline, ['USER', 'WEB', 'CLOUD'])
examples.add('dayline', 'show nr of lines spoken in last day', 'dl')
aliases.data['dl'] = 'dayline'

def handle_mono(bot, ievent):   
    """ mono [<nick>] .. show length of monologue """
    if not logs:
        ievent.reply('log plugin is not enabled')
        return
    if ievent.channel not in logs.loglist:
        ievent.reply('logging is not enabled in %s' % ievent.channel)
        return
    teller = 0
    skip = 0
    try:
        nick = ievent.args[0].lower() 
    except IndexError:
        nick = ievent.nick.lower()
    for i in logs.fromtime(ievent.channel, time.time() - 60*60):
        if i[4].startswith('CMND:'):
            continue
        if i[2].lower() == nick:
            teller += 1
        else:
            teller = 0
    if teller > 4:
        ievent.reply('%s lines of monologue' % teller)
    else:
        ievent.reply("%s is not making a monologue" % nick)

cmnds.add('mono', handle_mono, ['USER', 'CLOUD'])
examples.add('mono', 'mono [<nick>] .. show nr lines of monologue', \
'1) mono 2) mono dunker')
