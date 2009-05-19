# gozerbot/jabbermsg.py
#
#

""" jabber message definition .. types can be normal, chat, groupchat, 
    headline or  error
"""

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from gozerbot.generic import rlog, toenc, fromenc, jabberstrip, makeargrest, lockdec
from gozerbot.eventbase import EventBase

# basic imports
import xmpp, types, time, thread

# locks
replylock = thread.allocate_lock()
replylocked = lockdec(replylock)

class Jabbermsg(xmpp.Message, EventBase):

    """ jabber message object. """

    def __init__(self, msg=None):

        if msg:
            xmpp.Message.__init__(self, node=str(msg))
        else:
            xmpp.Message.__init__(self)

        EventBase.__init__(self)

        if msg:
            self.orig = msg

        self.jabber = True
        #self.id = self.getID()
        self.bot = None
        self.botoutput = False
        self.isresponse = False
        self.type = self.getType()

    @replylocked
    def reply(self, txt, result=None, nick=None, dot=False, nritems=False, nr=False, fromm=None, private=False):

        """ reply txt. """

        if result == []:
            return

        restxt = ""

        if type(result) == types.DictType:

            for i, j in result.iteritems():
                if type(j) == types.ListType:
                    try:
                        z = ' .. '.join(j)
                    except TypeError:
                        z = unicode(j)
                else:
                    z = j
                if dot == True:
                    restxt += "%s: %s %s " % (i, z, ' .. ')
                elif dot:
                    restxt += "%s: %s %s " % (i, z, dot)
                else:
                    restxt += "%s: %s " % (i, z)

            if restxt:
                if dot == True:
                    restxt = restxt[:-6]
                elif dot:
                    restxt = restxt[:-len(dot)]
        lt = False

        if type(txt) == types.ListType and not result:
            result = txt
            origtxt = ""
            lt = True
        else:
            origtxt = txt

        if result:
            lt = True

        if self.queues:
            for i in self.queues:
                if lt:
                    for j in result:
                        i.put_nowait(j)
                else:
                    i.put_nowait(txt)
            return

        pretxt = origtxt

        if lt and not restxt:
            res = []
            for i in result:
                if type(i) == types.ListType or type(i) == types.TupleType:
                    try:
                        res.append(' .. '.join(i))
                    except TypeError:
                        res.append(unicode(i))
                else:
                    res.append(i)
            result = res
            if nritems:
                if len(txt) > 1:
                    pretxt = "(%s items) .. " % len(result)
            txtlist = [unicode(i) for i in result]
            if not nr is False:
                try:
                    start = int(nr)
                except ValueError:
                    start = 0
                txtlist2 = []
                teller = start
                for i in txtlist:
                    txtlist2.append("%s) %s" % (teller, i))
                    teller += 1
                txtlist = txtlist2
            if dot == True:
                restxt = ' .. '.join(txtlist)
            elif dot:
                restxt = dot.join(txtlist)
            else:
                restxt = ' '.join(txtlist)

        if pretxt:
            restxt = pretxt + restxt

        txt = jabberstrip(restxt)

        if not txt:
            return

        what = txt
        txtlist = []
        start = 0
        end = 2000
        length = len(what)

        for i in range(length/end+1):
            endword = what.find(' ', end)
            if endword == -1:
                endword = end
            txtlist.append(what[start:endword])
            start = endword
            end = start + 2000

        size = 0

        # see if we need to store output in less cache
        if len(txtlist) > 1:
            self.bot.less.add(self.userhost, txtlist)
            size = len(txtlist) - 1
            result = txtlist[:1][0]
            if size:
                result += " (+%s)" % size
        else:
            result = txtlist[0]

        if self.filtered(result):
            return
        repl = self.buildReply(result)
        repl.setNamespace("jabber:client")

        if self.resource == 'jcoll':
            repl.setFrom(self.bot.jid.getStripped() + '/jcollres')
            repl.setTo(self.ruserhost.getStripped())
            self.bot.send(repl)
            return

        if self.groupchat:
            if self.resource == self.bot.nick:
                return
            if nick:
                repl.type = 'chat'
            elif private:
                repl.setTo(self.userhost)
            elif self.printto:
                repl.setTo(self.printto)
            else:
                repl.setTo(self.channel)

        if self.bot.google:
            repl.setFrom(self.bot.me)

        #if self.id:
        #    repl.setID(self.id)

        if not nick:
            repl.setType(self.type)
        self.bot.send(repl)

    def toirc(self, bot):

        """ set ircevent compat attributes. """

        self.jidchange = False
        self.cmnd = 'Message'
        self.conn = None
        self.prefix = ""
        self.postfix = ""
        self.target = ""
        self.arguments = []
        self.resource = fromenc(self.getFrom().getResource())
        self.channel = fromenc(self.getFrom().getStripped())
        self.origchannel = self.channel
        self.nick = self.resource
        self.user = ""

        try:
            self.jid = bot.jids[self.channel][self.resource]
            self.jidchange = True
        except KeyError:
            self.jid = self.getFrom()

        self.ruserhost = self.jid
        self.userhost = fromenc(str(self.jid))
        self.stripped = fromenc(self.jid.getStripped())
        self.printto = self.channel
        self.txt = jabberstrip(fromenc(self.getBody()))
        self.origtxt = self.txt
        self.to = fromenc(str(self.getTo()))
        self.time = time.time()
        self.args = []
        self.rest = ' '.join(self.args)
        self.usercmnd = 0
        self.isresponse = False
        self.bot = bot
        self.sock = None
        self.closequeue = False
        self.allowqueue = True
        self.inqueue = None
        self.queues = []
        self.speed = 5
        self.options = {}
        self.optionset = []
        self.groups = None
        self.type = self.getType()
        self.cc = ""
        self.alias = ""
        self.aliased = ""
        self.denied = False

        if self.type == 'groupchat':
            self.groupchat = True
            if self.jidchange:
                self.userhost = self.stripped
        else:
            self.groupchat = False
            self.userhost = self.stripped

        self.msg = not self.groupchat
        self.bot.nrevents += 1
        self.filter = []
