# gozerbot/jabberbot.py
#
#

""" jabber bot definition """

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from gozerbot.users import users
from gozerbot.monitor import jabbermonitor
from gozerbot.wait import Jabberwait, Jabbererrorwait
from gozerbot.generic import rlog, handle_exception, lockdec, waitforqueue, \
toenc, fromenc, jabberstrip, getrandomnick
from gozerbot.config import config
from gozerbot.plugins import plugins
from gozerbot.persist.pdod import Pdod
from gozerbot.utils.dol import Dol
from gozerbot.datadir import datadir
from gozerbot.channels import Channels
from gozerbot.less import Less
from gozerbot.ignore import shouldignore
from gozerbot.callbacks import jcallbacks
from gozerbot.threads.thr import start_new_thread
from gozerbot.fleet import fleet
from gozerbot.botbase import BotBase
from jabbermsg import Jabbermsg
from jabberpresence import Jabberpresence
from jabberiq import Jabberiq

# xmpp imports
from xmpp.simplexml import Node
import xmpp

# basic imports
import time, Queue, os, threading, thread, types, xml, re

# locks
jabberoutlock = thread.allocate_lock()
jabberinlock = thread.allocate_lock()
connectlock = thread.allocate_lock()
outlocked = lockdec(jabberoutlock)
inlocked = lockdec(jabberinlock)
connectlocked = lockdec(connectlock)

class Jabberbot(BotBase):

    """ jabber bot class. """

    def __init__(self, cfg):
        BotBase.__init__(self, cfg)
        if not self.port:
            self.port = 5222
        self.type = 'jabber'
        self.outqueue = Queue.Queue()
        self.sock = None
        self.me = None
        self.lastin = None
        self.test = 0
        self.connecttime = 0
        self.connection = None
        self.privwait = Jabberwait()
        self.errorwait = Jabbererrorwait()
        self.jabber = True
        self.connectok = threading.Event()
        self.jids = {}
        self.topics = {}
        self.timejoined = {}
        self.channels409 = []
        if not self.state.has_key('ratelimit'):
            self.state['ratelimit'] = 0.05
        if self.port == 0:
            self.port = 5222

    def _resumedata(self):

        """ return data needed for resuming. """

        return {self.name: [self.server, self.user, self.password, self.port]}

    def _doprocess(self):

        """ process requests loop. """

        while not self.stopped:
            try:
                time.sleep(0.01)
                res = self.connection.Process(1)
                if res:
                    self.lastin = time.time()
            except xmpp.StreamError, ex:
                if u'Disconnected' in str(ex):
                    rlog(10, self.name, str(ex))
                    self.reconnect()
            except xml.parsers.expat.ExpatError, ex:
                if u'not well-formed' in str(ex):
                    rlog(10, self.name, str(ex))
                    continue
            except xml.parsers.expat.ExpatError, ex:
                if u'duplicate attribute' in str(ex):
                    rlog(10, self.name, str(ex))
                    continue
            except Exception, ex:
                handle_exception()
                if not self.stopped:
                    time.sleep(1)
                else:
                    return

    def _outputloop(self):

        """ loop to take care of output to the server. """

        rlog(10, self.name, 'starting outputloop')

        while not self.stopped:
            what = self.outqueue.get()
            if self.stopped or what == None:
                 break
            self.rawsend(what)
            sleeptime = self.cfg['jabberoutsleep'] or config['jabberoutsleep']
            if not sleeptime:
                sleeptime = 0.2
            rlog(-10, self.name, 'jabberoutsleep .. sleeping %s seconds' % sleeptime)
            time.sleep(sleeptime)

        rlog(10, self.name, 'stopping outputloop')

    def _keepalive(self):

        """ keepalive method .. send empty string to self every 3 minutes. """

        nrsec = 0

        while not self.stopped:
            time.sleep(1)
            nrsec += 1
            if nrsec < 180:
                continue
            else:
                nrsec = 0
            self.say(self.me, "")

    def _keepchannelsalive(self):

        """ channels keep alive method. """

        nrsec = 0

        while not self.stopped:
            time.sleep(1)
            nrsec += 1
            if nrsec < 600:
                continue
            else:
                nrsec = 0
            for i in self.state['joinedchannels']:
                if i not in self.channels409:
                    self.say(i, "")

    @connectlocked
    def _connect(self, reconnect=True):

        """ connect to server .. start read loop. """

        try:
            self.username = self.user.split('@')[0]
        except ValueError:
            raise Exception("i need config user with a @ in it")

        self.me = self.user
        self.jid = xmpp.JID(self.user)
        self.server = self.jid.getDomain()
        self.nick = self.username
        rlog(10, self.name, 'connecting to %s' % self.server)

        if config['debug']:
            self.connection = xmpp.Client(self.server, debug=['always', 'nodebuilder'])
        else:
            self.connection = xmpp.Client(self.server, debug=[])

        time.sleep(2)

        try:
            try:
                import DNS
                self.connection.connect()
            except (ImportError, ValueError):
                if config['debug']:
                    self.connection = xmpp.Client(self.server, debug=['always', 'nodebuilder'])
                else:
                    self.connection = xmpp.Client(self.server, debug=[])
                self.connection.connect((self.host, self.port))
        except AttributeError:
            handle_exception()
            rlog(10, self.name, "can't connect to %s" % self.host)
            return

        if not self.connection:
            rlog(10, self.name, "can't connect to %s" % self.host)
            return

        try:
            rlog(10, self.name, 'doing auth')
            auth = self.connection.auth(self.username, self.password, \
'gozerbot')
        except AttributeError:
            #handle_exception()
            rlog(10, self.name, "can't auth to %s" % self.host)
            return

        if not auth:
            rlog(10, self.name, 'auth for %s failed .. trying register' \
% self.username)
            info = {'username': self.username, 'password': self.password}
            xmpp.features.getRegInfo(self.connection, self.host, info)
            if not xmpp.features.register(self.connection, self.host, info):
                rlog(100, self.name, "can't register")
                return
            else:
                self.connection = xmpp.Client(self.server, debug=[])
                self.connection.connect((self.host, self.port))
                auth = self.connection.auth(self.username, self.password, 'gozerbot')
                rlog(100, self.name, "register succeded")
        self.connecttime = time.time()
        rlog(100, self.name, 'connected! type: %s' % \
self.connection.connected)
        self.connection.RegisterHandler('message', self.messageHandler)
        self.connection.RegisterHandler('presence', self.presenceHandler)
        self.connection.RegisterHandler('iq', self.iqHandler)
        self.connection.UnregisterDisconnectHandler(\
self.connection.DisconnectHandler)
        self.connection.RegisterDisconnectHandler(self.disconnectHandler)
        self.connection.UnregisterHandlerOnce = self.UnregisterHandlerOnce
        self.stopped = 0
        jabbermonitor.start()
        start_new_thread(self._doprocess, ())
        start_new_thread(self._keepalive, ())
        start_new_thread(self._outputloop, ())
        start_new_thread(self._keepchannelsalive, ())
        self.connection.sendInitPresence()
        #self.connection.getRoster()
        self.connectok.set()
        return 1

    def connect(self, reconnect=True):

        """ connect to the server. """

        res = 0

        try:
            res = self._connect(reconnect)
        #except AttributeError:
        #    rlog(10, self.name, "%s denied the connection" % self.host)
        #    return
        except Exception, ex:
            if self.stopped:
                return 0
            handle_exception()
            if reconnect:
                return self.reconnect()

        if res:
            fleet.addbot(self)

        return res

    def joinchannels(self):

        """ join all already joined channels """

        for i in self.state['joinedchannels']:
            key = self.channels.getkey(i)
            nick = self.channels.getnick(i)
            result = self.join(i, key, nick)

            if result == 1:
                rlog(10, self.name, 'joined %s' % i)
            else:
                rlog(10, self.name, 'failed to join %s: %s' % (i, result))


    def broadcast(self, txt):

        """ broadcast txt to all joined channels. """

        for i in self.state['joinedchannels']:
            self.say(i, txt)

    def sendpresence(self, to):

        """ send presence. """

        presence = xmpp.Presence(to=to)
        presence.setFrom(self.me)
        self.send(presence)

    def iqHandler(self, conn, node):

        """ handle iq stanza's. """

        rlog(5, self.name, str(node))
        iq = Jabberiq(node)
        iq.toirc(self)
        jcallbacks.check(self, iq)

    def messageHandler(self, conn, msg):

        """ message handler. """

        rlog(5, self.name, 'incoming: %s' % str(msg))

        if self.test:
            return

        if 'jabber:x:delay' in str(msg):
            return

        m = Jabbermsg(msg)
        m.toirc(self)

        if m.groupchat and m.getSubject():
            self.topiccheck(m)
            nm = Jabbermsg(msg)
            nm.copyin(m)
            print nm
            jcallbacks.check(self, nm)
            return

        self.privwait.check(m)

        if m.isresponse:
            return

        if not m.txt:
            return

        if self.me in m.userhost:
            return 0

        if m.groupchat and self.nick == m.resource:
            return 0
        go = 0

        try:
            cc = self.channels[m.channel]['cc']
        except (TypeError, KeyError):
            cc = config['defaultcc'] or '!'

        try:
            channick = self.channels[m.channel]['nick']
        except (TypeError, KeyError):
            channick = self.nick

        if m.msg and not config['noccinmsg']:
            go = 1
        elif m.txt[0] in cc:
            go = 1
        elif m.txt.startswith("%s: " % channick):
            m.txt = m.txt.replace("%s: " % channick, "")
            go = 1
        elif m.txt.startswith("%s, " % channick):
            m.txt = m.txt.replace("%s, " % channick, "")
            go = 1

        if m.txt[0] in cc:
            m.txt = m.txt[1:]

        if go:
            try:
                if plugins.woulddispatch(self, m):
                    m.usercmnd = True
                plugins.trydispatch(self, m)
            except:
                handle_exception()

        try:
            nm = Jabbermsg(msg)
            nm.copyin(m)
            jcallbacks.check(self, nm)
            if nm.getType() == 'error':
                err = nm.getErrorCode()
                if err:
                    rlog(10, self.name + '.error', "%s => %s: %s" % (nm.getFrom(),\
 err, nm.getError()))
                    rlog(10, self.name + '.error', str(nm))
                self.errorwait.check(nm)
                try:
                   method = getattr(self,'handle_' + err)
                   # try to call method
                   try:
                       method(nm)
                   except:
                       handle_exception()
                except AttributeError:
                    # no command method to handle event
                    pass

        except Exception, ex:
            handle_exception()
 
    def handle_409(self, event):

        """ handle 409 errors .. 409 is occupant already in room. """

        if event.type == 'Presence':
            if event.jid in self.state['joinedchannels']:
                rnick = getrandomnick()
                rlog(10, self.name, 'using random nick %s to join %s' % (rnick, event.channel))
                self.join(event.channel, nick=getrandomnick())

    def presenceHandler(self, conn, pres):

        """ overloaded presence handler. """

        rlog(5, self.name, 'incoming: %s' % str(pres))
        p = Jabberpresence(pres)
        p.toirc(self)
        frm = p.getFrom()
        nickk = ""
        nick = frm.getResource()

        if nick:
            self.userhosts[nick] = str(frm)
            nickk = nick

        jid = None

        for i in p.getPayload():
            try:
                if i.getName() == 'x':
                    for j in i.getPayload():
                        if j.getName() == 'item':
                            attrs = j.getAttrs()
                            if attrs.has_key('jid'):
                                jid = xmpp.JID(attrs['jid'])
            except AttributeError:
                continue

        if nickk and jid:
            channel = frm.getStripped()
            if not self.jids.has_key(channel):
                self.jids[channel] = {}
            self.jids[channel][nickk] = jid
            self.userhosts[nickk.lower()] = str(jid)
            rlog(0, self.name, 'setting jid of %s (%s) to %s' % (nickk, \
 channel, jid))

        if p.type == 'subscribe':
            fromm = p.getFrom()
            self.send(xmpp.Presence(to=fromm, typ='subscribed'))
            self.send(xmpp.Presence(to=fromm, typ='subscribe'))

        nick = p.resource

        if p.type != 'unavailable':
            self.userchannels.adduniq(nick, p.channel)
            p.joined = True
        elif self.me in p.userhost:
            try:
                del self.jids[p.channel]
                rlog(10, self.name, 'removed %s channel jids' % p.channel)
            except KeyError:
                pass
        else:
            try:
                del self.jids[p.channel][p.nick]
                rlog(10, self.name, 'removed %s jid' % p.nick)
            except KeyError:
                pass

        p.conn = conn
        jcallbacks.check(self, p)

        if p.getType() == 'error':
            err = p.getErrorCode()

            if err:
                rlog(10, self.name + '.error', "%s => %s: %s" % (p.getFrom(),\
 err, p.getError()))
                rlog(10, self.name + '.error', str(p))

            self.errorwait.check(p)

            try:
                method = getattr(self,'handle_' + err)
                # try to call method
                try:
                    method(p)
                except:
                    handle_exception()
            except AttributeError:
                # no command method to handle event
                pass

    def reconnect(self):

        """ reconnect to the server. """

        rlog(100, self.name, 'reconnecting .. sleeping 15 seconds')
        self.exit()
        time.sleep(15)
        newbot = Jabberbot(self.cfg)

        if newbot.connect():
            newbot.joinchannels()

        fleet.replace(self.name, newbot)
        return 1

    def disconnectHandler(self):

        """ overloaded disconnect handler. """

        rlog(100, self.name, "disconnected")

        if not self.stopped:
            self.reconnect()
        else:
            self.exit()

    def send(self, what):

        """ send stanza to the server. """

        if self.stopped:
           return
        self.outqueue.put(toenc(what))
        jabbermonitor.put(self, unicode(what))

    @outlocked
    def rawsend(self, what):

        """ do a direct send. """

        try:
            rlog(2, self.name, u"rawsend: %s" % unicode(jabberstrip(what)))
            if self.connection.isConnected():
                self.connection.send(what)
        except:
            handle_exception()
    
    def sendnocb(self, what):

        """ send to server without calling callbacks/monitors """

        if self.stopped:
            return
        self.outqueue.put(toenc(what))

    def action(self, printto, txt, fromm=None, groupchat=True):

        """ send an action. """

        txt = "/me " + txt

        if self.google:
            fromm = self.me

        if printto in self.state['joinedchannels'] and groupchat:
            message = xmpp.Message(to=printto, body=txt, typ='groupchat')
        else:
            message = xmpp.Message(to=printto, body=txt)

        if fromm:
            message.setFrom(fromm)

        self.send(message)
        
    def say(self, printto, txt, fromm=None, groupchat=True, speed=5, type="normal", how=''):

        """ say txt to channel/JID. """

        txt = jabberstrip(txt)

        if self.google:
            fromm = self.me

        if printto in self.state['joinedchannels'] and groupchat:
            message = xmpp.Message(to=printto, body=txt, typ='groupchat')
        else:
            message = xmpp.Message(to=printto, body=txt, typ=type)

        if fromm:
            message.setFrom(fromm)

        self.send(message)

    def saynocb(self, printto, txt, fromm=None, groupchat=True, speed=5, type="normal", how=''):

        """ say txt to channel/JID without calling callbacks/monitor. """

        txt = jabberstrip(txt)

        if self.google:
            fromm = self.me

        if printto in self.state['joinedchannels'] and groupchat:
            message = xmpp.Message(to=printto, body=txt, typ='groupchat')
        else:
            message = xmpp.Message(to=printto, body=txt, typ=type)

        self.sendnocb(message)

    def wait(self, msg, txt):

        """ wait for user response. """

        msg.reply(txt)
        queue = Queue.Queue()
        self.privwait.register(msg, queue)
        result = queue.get()

        if result:
            return result.getBody()

    def save(self):

        """ save bot's state. """

        self.state.save()

    def quit(self):

        """ send unavailable presence. """

        try:
            presence = xmpp.Presence()
        except ValueError:
            return

        presence.setType('unavailable')

        for i in self.state['joinedchannels']:
            presence.setTo(i)
            self.send(presence)

        presence = xmpp.Presence()
        presence.setFrom(self.me)
        presence.setType('unavailable')
        self.send(presence)
        time.sleep(1)
        
    def exit(self):

        """ exit the bot. """

        self.quit()
        self.stopped = 1
        self.outqueue.put_nowait(None)
        self.save()
        rlog(10, self.name, 'exit')

    def join(self, channel, password=None, nick=None):

        """ join conference. """

        if '#' in channel:
            return

        try:
            if not nick:
                nick = channel.split('/')[1]
        except IndexError:
            nick = self.nick

        channel = channel.split('/')[0]

        if not self.channels.has_key(channel):
            # init channel data
            self.channels.setdefault(channel, {})

        # setup error wait
        q = Queue.Queue()
        self.errorwait.register("409", q, 3)
        self.errorwait.register("401", q, 3)
        self.errorwait.register("400", q, 3)
        # do the actual join
        presence = xmpp.Presence(to=channel + '/' + nick)
        #presence.setFrom(self.me)

        if password:
            passnode = Node('password')
            passnode.addData(password)
            presence.addChild(name='x', namespace='http://jabber.org/protocol/muc', \
payload=[passnode, ])

        self.send(presence)
        errorobj = waitforqueue(q, 3)

        if errorobj:
            err = errorobj[0].error
            rlog(10, self.name, 'error joining %s: %s' % (channel, err))
            if err == '409':
                if channel not in self.channels409:
                    self.channels409.append(channel)
            return err

        self.timejoined[channel] = time.time()
        chan = self.channels[channel]
        # if password is provided set it
        chan['nick'] = nick

        if password:
            chan['key'] = password

        # check for control char .. if its not there init to !
        if not chan.has_key('cc'):
            chan['cc'] = config['defaultcc'] or '!'

        if not chan.has_key('perms'):
            chan['perms'] = []

        self.channels.save()

        if channel not in self.state['joinedchannels']:
            self.state['joinedchannels'].append(channel)

        if channel in self.channels409:
            self.channels409.remove(channel)

        self.state.save()
        return 1

    def part(self, channel):
 
        """ leave conference. """

        if '#' in channel:
            return

        presence = xmpp.Presence(to=channel)
        presence.setFrom(self.me)
        presence.setType('unavailable')
        self.send(presence)

        if channel in self.state['joinedchannels']:
            self.state['joinedchannels'].remove(channel)

        self.state.save()
        return 1

    def outputnolog(self, printto, what, how, who=None, fromm=None):

        """ do output but don't log it. """

        if fromm and shouldignore(fromm):
            return

        self.saynocb(printto, what)

    def topiccheck(self, msg):

        """ chek if topic is set. """

        if msg.groupchat:
            try:
                topic = msg.getSubject()
                if not topic:
                    return None
                self.topics[msg.channel] = (topic, msg.userhost, time.time())
                rlog(10, self.name, 'topic of %s set to %s' % \
(msg.channel, topic))
            except AttributeError:
                return None

    def settopic(self, channel, txt):

        """ set topic. """

        pres = xmpp.Message(to=channel, subject=txt)
        pres.setType('groupchat')
        self.send(pres)

    def gettopic(self, channel):

        """ get topic. """

        try:
            topic = self.topics[channel]
            return topic
        except KeyError:
            return None

    def UnregisterHandlerOnce(self, a, b, xmlns=None):

        """ hack to work around missing method. """

        print a, b

    def sendraw(self, msg):

        """ send a msg directly on the socket or connection. """

        rlog(2, self.name, u"sendraw: %s" % unicode(msg))

        if self.connection:
            try:
                if self.connection.__dict__.has_key('TCPsocket'):
                    self.connection.TCPsocket.send(msg)
                else:
                    self.connection.Connection.send(msg)
            except:
                handle_exception()

    def domsg(self, msg):

        """ dispatch an msg on the bot. """

        plugins.trydispatch(self, msg)
