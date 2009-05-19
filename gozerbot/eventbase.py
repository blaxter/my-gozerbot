# gozerbot/eventbase.py
#
#

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from generic import rlog, stripident, fix_format, fromenc, toenc
from gozerbot.stats import stats

# basic imports
import time, re, types, copy

# used to copy data
cpy = copy.deepcopy


def makeargrest(event):
    """ set arguments and rest attributes of an event. """

    # arguments 
    try:
        event.args = event.txt.split()[1:]
    except ValueError:
        event.args = []

    # txt after command
    try:
        cmnd, event.rest = event.txt.split(' ', 1)
    except ValueError:
        event.rest = ""   

    # the command 
    event.command = event.txt.split(' ')[0]

class EventBase(object):

    def __init__(self, event=None):
        self.orig = None # the original command if 
        self.type = 'chat' # type of event
        self.jabber = False # set if event is jabber event
        self.groupchat = False # set if event is groupchat
        self.botoutput = False # set if event is bot output
        self.cmnd = None # the event command
        self.prefix = u"" # txt before the command
        self.postfix = u"" # txt after the command
        self.target = u"" # target to give reposnse to
        self.arguments = [] # arguments of event
        self.nick = u"" # nick of user originating the event 
        self.user = u""  # user originating the event
        self.ruserhost = u"" # real userhost 
        self.userhost = u"" # userhost that might change
        self.stripped = u"" # stripped JID 
        self.resource = u"" # resource part of JID
        self.origchannel = u"" # original channel
        self.channel = u"" # channel .. might change
        self.origtxt = u"" # original txt
        self.txt = u"" # text .. might change
        self.command = u"" # the bot command if any
        self.alias = u"" # set to alias if one is used
        self.aliased = u"" # set if commadn is aliased
        self.time = time.time() # event creation time
        self.msg = False # set if event is a private message
        self.args = [] # arguments of command
        self.rest = u"" # txt following the command
        self.usercmnd = 0 # set if event is a command
        self.bot = None # the bot where the event originated on
        self.sock = None # socket (set in DCC chat)
        self.allowqueue = True # allow event to be used in pipeline
        self.closequeue = True # cloase event queues when execution has ended
        self.inqueue = None # queue used as input in pipeline
        self.queues = [] # output queues (only used when set)
        self.printto = None # target to printti
        self.speed = 0 # speed with which this event needs to be processed
        self.groups = None # set if event triggers a RE callback
        self.cc = u"" # control character
        self.jid = None # JID of used originating the event
        self.jidchange = None # set is event changes jid
        self.conn = None # connection of bot originating the event
        self.to = None  # target
        self.denied = False # set if command is denied
        self.isresponse = False # set if event is a reponse
        self.isdcc = False # set if event is DCC related
        self.options = {} # options dict on the event
        self.optionset = [] # list of options set
        self.filter = [] # filter list to use on output
 
        # if event is provided inititalise this object with it
        if event:
            self.copyin(event)

        # stats
        stats.up('events', 'created')

    def copyin(self, ievent):

        """ copy in an event. """

        self.orig = cpy(ievent.orig)
        self.cmnd = cpy(ievent.cmnd)
        self.type = cpy(ievent.type)
        self.groupchat = cpy(ievent.groupchat)
        self.prefix = cpy(ievent.prefix)
        self.postfix = cpy(ievent.postfix)
        self.target = cpy(ievent.target)
        self.arguments = list(ievent.arguments)
        self.nick = cpy(ievent.nick)
        self.user = cpy(ievent.user)
        self.ruserhost = cpy(ievent.ruserhost)
        self.userhost = cpy(ievent.userhost)
        self.stripped = cpy(ievent.stripped)
        self.resource = cpy(ievent.resource)
        self.origchannel = cpy(ievent.origchannel)
        self.channel = cpy(ievent.channel)
        self.origtxt = cpy(ievent.origtxt)
        self.txt = cpy(ievent.txt)
        self.command = cpy(ievent.command)
        self.alias = cpy(ievent.alias)
        self.aliased = cpy(ievent.aliased)
        self.time = ievent.time
        self.msg = cpy(ievent.msg)
        self.args = list(ievent.args)
        self.rest = cpy(ievent.rest)
        self.usercmnd = cpy(ievent.usercmnd)
        self.bot = ievent.bot
        self.sock = ievent.sock
        self.printto = ievent.printto
        self.speed = int(ievent.speed)
        self.inqueue = ievent.inqueue
        self.allowqueue = cpy(ievent.allowqueue)
        self.closequeue = cpy(ievent.closequeue)
        self.queues = list(ievent.queues)
        self.cc = cpy(ievent.cc)
        self.jid = ievent.jid
        self.jidchange = ievent.jidchange
        self.conn = ievent.conn
        self.to = ievent.to
        self.denied = ievent.denied
        self.options = dict(ievent.options)
        self.optionset = list(ievent.optionset)
        self.filter = list(ievent.filter)
        self.groupchat = cpy(ievent.groupchat)
        self.jabber = bool(ievent.jabber)
        self.botoutput = cpy(ievent.botoutput)
        self.isresponse = cpy(ievent.isresponse)
        self.isdcc = cpy(ievent.isdcc)

    def __str__(self):

        """ return a string representation of the event. """

        return "cmnd=%s prefix=%s postfix=%s arguments=%s nick=%s user=%s userhost=%s channel=%s txt='%s' command=%s args=%s rest=%s speed=%s options=%s" % (self.cmnd, self.prefix, self.postfix, self.arguments, self.nick, self.user, self.userhost, self.channel, self.txt, self.command, self.args, self.rest, self.speed, self.options)

    def filtered(self, txt):

        """ see if txt if filtered on this event. """
        if not self.filter:
            return False
        for filter in self.filter:
            if filter in txt:
                return False
        return True

    def parse(self, bot, rawstr):

        """ parse raw string into event. """

        pass

    def reply(self, txt, result=None, nick=None, dot=False, nritems=False, nr=False, fromm=None, private=False, how=''):

        # don't replu is result is empty list
        if result == []:
            return

        # stats
        stats.up('events', 'replies')
        if not how:
            try:
                how = self.options['--how']        
            except KeyError:
                how = 'msg'

        # init
        restxt = ""
        splitted = []

        # make reply if result is a dict
        if type(result) == types.DictType:
            for i, j in result.iteritems():
                if type(j) == types.ListType:
                    try:
                        z = ' .. '.join(j)
                    except TypeError:
                        z = unicode(j)
                else:
                    z = j
                res = "%s: %s" % (i, z)
                splitted.append(res)
                if dot == True:
                    restxt += "%s%s" % (res, ' .. ')
                else:
                    restxt += "%s %s" % (dot or ' ', res)
            if restxt:
                if dot == True:
                    restxt = restxt[:-6]
                elif dot:
                    restxt = restxt[:-len(dot)]

        lt = False # set if result is list

        # set vars if result is a list
        if type(txt) == types.ListType and not result:
            result = txt
            origtxt = u""
            lt = True
        else:
            origtxt = txt

        if result:
            lt = True

        # if queues are set write output to them
        if self.queues:
            for i in self.queues:
                if splitted:
                    for item in splitted:
                        i.put_nowait(item)
                elif restxt:
                    i.put_nowait(restxt)
                elif lt:
                    for j in result:
                        i.put_nowait(j)
                else:
                    i.put_nowait(txt)
            return

        # check if bot is set in event
        if not self.bot:
            rlog(10, 'event', 'no bot defined in event')
            return

        # make response
        pretxt = origtxt
        if lt and not restxt:
            res = []

            # check if there are list in list
            for i in result:
                if type(i) == types.ListType or type(i) == types.TupleType:
                    try:
                        res.append(u' .. '.join(i))
                    except TypeError:
                        res.extend(i)
                else:
                    res.append(i)

            # if nritems is set ..
            result = res
            if nritems:
                if len(result) > 1:
                    pretxt += "(%s items) .. " % len(result)
            txtlist = result

            # prepend item number for results
            if not nr is False:
                try:
                    start = int(nr)
                except ValueError:
                    start = 0
                txtlist2 = []
                teller = start
                for i in txtlist:
                    txtlist2.append(u"%s) %s" % (teller, i))
                    teller += 1
                txtlist = txtlist2

            # convert results to encoding
            txtl = []
            for item in txtlist:
                txtl.append(toenc(item))
            txtlist = txtl

            # join result with dot 
            if dot == True:
                restxt = ' .. '.join(txtlist)
            elif dot:
                restxt = dot.join(txtlist)
            else:
                restxt = ' '.join(txtlist)

        # see if txt needs to be prepended
        if pretxt:
            try:
                restxt = pretxt + restxt
            except TypeError:
                rlog(10, 'eventbase', "can't add %s and %s" % (str(pretxt), str(restxt)))

        # if txt in result is filtered ignore the reuslt
        if self.filtered(restxt):
            return

        # if event is DCC based write result directly to socket
        if self.cmnd == 'DCC' and self.sock:
            self.bot.say(self.sock, restxt, speed=self.speed, how=how)
            return

        # if nick is set write result to nick in question
        if nick:
            self.bot.say(nick, restxt, fromm=nick, speed=self.speed, how=how)
            return

        # if originatiog event is a private message or private flaf is set 
        if self.msg or private:
            self.bot.say(self.nick, restxt, fromm=self.nick, speed=self.speed, how=how)
            return

        # check if bot is in silent mode .. if so use /msg 
        silent = False
        channel = self.printto or self.channel
        try:
            silent = self.bot.channels[channel]['silent']
        except (KeyError, TypeError):
            pass
        fromm = fromm or self.nick

        # check if notice needs to be used
        if silent:
            notice = False
            try:
                notice = self.bot.channels[channel]['notice']
            except (KeyError, TypeError):
                pass
            if notice:
                self.bot.say(self.nick, restxt, how='notice', fromm=fromm, speed=self.speed)
            else:
                self.bot.say(self.nick, restxt, fromm=fromm, speed=self.speed, how=how)
            return

        # if printto is set used that as the target
        if self.printto:
            self.bot.say(self.printto, restxt, fromm=fromm, speed=self.speed, how=how)
            return
        else:
            self.bot.say(self.channel, restxt, fromm=fromm, speed=self.speed, how=how)

    def missing(self, txt):

        """ show what arguments are missing. """

        stats.up('events', 'missing')
        if self.origtxt:
            splitted = self.origtxt.split()
            if self.bot.nick in splitted[0]:
                try:
                    cmnd = splitted[1]
                except IndexError:
                    cmnd = splitted[0]
            elif 'cmnd' in splitted[0]:
                try:
                    cmnd = splitted[2]
                except IndexError:
                    cmnd = splitted[0]
            else:
                if self.msg:
                    cmnd = splitted[0]
                else:
                    if self.aliased:
                        cmnd = self.aliased
                    else:
                        cmnd = splitted[0][1:]
            self.reply(cmnd + ' ' + txt)
        else:
            self.reply('missing origtxt: %s' % txt)

# default event used to initialise events
defaultevent = EventBase()
