# gozerbot/botbase.py
#
#

""" bot base class. provides data/methods common to all bots. """

# gozerbot imports
from generic import rlog
from less import Less
from persist.pdol import Pdol
from utils.dol import Dol
from persist.persiststate import PersistState
from channels import Channels
from datadir import datadir
from persist.pdod import Pdod
from config import config
from runner import runners_start
from gozerbot.plugins import plugins
from gozerbot.cache import userhosts

# basic imports
import time, threading, os, types

class BotBase(object):

    def __init__(self, cfg):

        # set attributes based on config 
        self.__dict__.update(cfg)
        # if name not set in config file use the directory name
        if not cfg.has_key('name'):
            self.name = cfg.dir.split(os.sep)[-1]
        # default nick to gozerbot
        if not cfg.has_key('nick'):
            self.nick = 'gozerbot'
        # default port to 0 (use default port)
        if not cfg.has_key('port'):
            self.port  = 0
        # make sure bot name is not a directory
        if '..' in self.name or '/' in self.name:
            raise Exception('wrong bot name %s' % self.name)
        # set datadir to datadir/fleet/<botname>
        self.datadir = datadir + os.sep + 'fleet' + os.sep + self.name
        # bot state
        self.state = Pdod(self.datadir + os.sep + 'state') # bot state
        # joined channels list .. used to join channels
        if not self.state.has_key('joinedchannels'):
            self.state['joinedchannels'] = []
        # allowed commands on the bot
        if not self.state.has_key('allowed'):
            self.state['allowed'] = []
        # channels we dont want ops in
        if not self.state.has_key('no-op'):
            self.state['no-op'] = []
        # channels we are op in
        if not self.state.has_key('opchan'):
            self.state['opchan'] = []
        self.cfg = cfg # the bots config
        self.orignick = "" # original nick
        self.blocking = True # use blocking sockets
        self.lastoutput = 0 # time of last output
        self.stopped = False # flag to set when bot is to be stopped
        self.connected = False # conencted flag
        self.connecting = False # connecting flag
        self.connectok = threading.Event() # event set when bot has connected
        self.waitingforconnect = False # flag to indicate we are waiting for connect
        self.starttime = time.time() # start time of the bot
        self.nrevents = 0 # number of events processed
        self.gcevents = 0 # number of garbage collected events
        self.less = Less(5) # output buffering
        self.userchannels = Dol() # list of channels a user is in
        self.channels = Channels(self.datadir + os.sep + 'channels') # channels
        self.userhosts = PersistState(self.datadir + os.sep + 'userhosts') # userhosts cache
        self.splitted = [] # list of splitted nicks
        self.throttle = [] # list of nicks that need to be throttled
        self.jabber = False # flag is set on jabber bots
        self.google = False # flag is set on google bots

        # start runners
        runners_start()

    def ownercheck(self, ievent, txt=None):

        """ check whether an event originated from the bot owner. """

        # use owner set in bot's config or else in global config
        owner = self.cfg['owner'] or config['owner']

        # check if event userhost in in owner .. check lists and string values
        if type(owner) == types.ListType:           
            if ievent.userhost in owner:            
                return 1
        elif owner == ievent.userhost:              
            return 1    
        else:
            rlog(100, self.name, 'failed owner check %s should be in %s' % (ievent.userhost, owner))
            if not txt:
                ievent.reply("only owner (see config file) is allowed to perform this command")
            else:
                ievent.reply("only owner (see config file) %s" % txt)
            return 0

    def save(self):

        """ save bot state. """

        self.channels.save()
        self.userhosts.save()
        self.state.save()

    def stop(self):

        """ stop the bot. """

        self.stopped = True
        rlog(10, self.name, 'stopped')

    def exit(self):

        """ shutdown the bot. overload this. """

        pass

    def connect(self, reconnect=True):

        """ connect the bot to the server. reconnects in the default case. """

        pass

    def joinchannels(self):

        """ join all registered channels. overload this. """

        pass

    def connectwithjoin(self, reconnect=True):

        """ connect to the server and join channels. """

        self.connect(reconnect)
        self.connectok.wait()
        self.joinchannels()

    def broadcast(self):

        """ announce a message to all channels. overload this"""

        pass

    def send(self, txt):

        """ send txt to the server. overload this"""

        pass

    def shutdown(self):

        """ close sockets of the bot. overload this"""

        pass

    def domsg(self, msg):

        """ excecute a message (txt line) on the bot. """ 

        plugins.trydispatch(self, msg)
