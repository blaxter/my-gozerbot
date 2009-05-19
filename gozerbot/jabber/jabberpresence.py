# gozerbot/jabberpresence.py
#
#

""" jabber presence definition """

__copyright__ = 'this file is in the public domain'

from gozerbot.generic import rlog
from gozerbot.irc.ircevent import makeargrest
import xmpp, time

class Jabberpresence(xmpp.Presence):

    """ jabber presence object """

    def __init__(self, msg=None):
        if msg:
            xmpp.Presence.__init__(self, node=msg)
        else:
            xmpp.Presence.__init__(self)
        self.jabber = True
        self.botoutput = False
        self.id = self.getID()
        rlog(1, 'jabberpresence', str(self))

    def toirc(self, bot):
        """ set ircevent compatible attributes """
        self.cmnd = 'Presence'
        self.conn = None
        self.prefix = ""
        self.postfix = ""
        self.target = ""
        self.arguments = []
        self.nick = str(self.getFrom().getResource())
        self.user = ""
        self.jid = self.getAttr('jid') or self.getFrom()
        self.ruserhost = self.jid
        self.userhost = str(self.jid)
        self.resource = self.getFrom().getResource()
        self.stripped = str(self.jid.getStripped())
        self.channel = str(self.getFrom().getStripped())
        self.printto = self.channel
        self.txt = ""
        self.origtxt = self.txt
        self.to = str(self.getTo())
        self.time = time.time()
        self.msg = None
        self.args = []
        self.rest = ' '.join(self.args)
        self.usercmnd = 0
        self.bot = bot
        self.sock = None
        self.inqueue = None
        self.queues = []
        self.printto = None
        self.speed = 5
        self.options = []
        self.groups = None
        self.type = self.getType()
        self.cc = ""
        self.alias = ""
        if self.type == 'groupchat':
            self.groupchat = True
        else:
            self.groupchat = False
        if self.txt:
            makeargrest(self)
        self.joined = False
        self.denied = False
 
    def copyin(self, jmsg):
        """ copy in another jabber presence """
        self.cmnd = str(jmsg.cmnd)
        self.conn = jmsg.conn
        self.prefix = str(jmsg.prefix)
        self.postfix = str(jmsg.postfix)
        self.target = str(jmsg.target)
        self.arguments = str(jmsg.arguments)
        self.nick = str(jmsg.nick)
        self.user = str(jmsg.user)
        if not jmsg.jid:
            self.jid = xmpp.JID(jmsg.userhost)
        else:
            self.jid = jmsg.jid
        self.ruserhost = str(jmsg.ruserhost)
        self.userhost = str(jmsg.userhost)
        self.resource = str(jmsg.resource)
        self.stripped = jmsg.stripped
        self.channel = str(jmsg.channel)
        self.printto = str(jmsg.printto)
        self.txt = str(jmsg.txt)
        self.origtxt = str(jmsg.origtxt)
        self.to = str(jmsg.to)
        self.time = jmsg.time
        self.msg = jmsg.msg
        self.args = list(jmsg.args)
        self.rest = str(jmsg.rest)
        self.usercmnd = jmsg.usercmnd
        self.bot = jmsg.bot
        self.sock = jmsg.sock
        self.inqueue = jmsg.inqueue
        self.queues = list(jmsg.queues)
        self.printto = jmsg.printto
        self.speed = int(jmsg.speed)
        self.options = jmsg.options
        self.groups = jmsg.groups
        self.groupchat = jmsg.groupchat
        self.cc = str(jmsg.cc)
        self.alias = str(jmsg.alias)
        self.joined = jmsg.joined
        self.denied = jmsg.denied

    def ircstr(self):
        """ return ircevent repr compatible string """
        return "cmnd=%s printto=%s arguments=%s nick=%s user=%s \
userhost=%s channel=%s txt=%s args=%s rest=%s speed=%s" % (self.cmnd, \
self.printto, self.arguments, self.nick, self.user, \
self.userhost, self.channel, self.txt, self.args, self.rest, self.speed)
