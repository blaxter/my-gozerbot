# gozerbot/fleet.py
#
#

""" fleet is a list of bots. """

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from gozerbot.datadir import datadir
from utils.exception import handle_exception
from utils.generic import waitforqueue
from utils.log import rlog
from threads.thr import start_new_thread, threaded
from config import Config, fleetbotconfigtxt, config
from users import users
from plugins import plugins
from simplejson import load

# basic imports
import Queue, os, types, threading, time, pickle, glob, logging, shutil

class Fleet(object):

    """ a fleet contains multiple bots (list of bots). """

    def __init__(self):
        self.datadir = datadir + os.sep + 'fleet'
        if not os.path.exists(self.datadir):
             os.mkdir(self.datadir)
        self.startok = threading.Event()
        self.bots = []

    def getfirstbot(self):

        """ return the main bot of the fleet. """

        return self.bots[0]
        
    def size(self):

        """ return number of bots in fleet. """

        return len(self.bots)

    def resume(self, sessionfile):

        """ resume bot from session file. """

        # read JSON session file
        session = load(open(sessionfile))

        #  resume bots in session file
        for name in session['bots'].keys():
            reto = None
            if name == session['name']:
                reto = session['channel']
            start_new_thread(self.resumebot, (name, session['bots'][name], reto))

        # allow 5 seconds for bots to resurrect
        time.sleep(5)

        # set start event
        self.startok.set()

    def makebot(self, name, cfg=None):

        """ create a bot with name .. use configuration is provided. """

        bot = None

        # if not config create a default bot
        if not cfg:
            cfg = Config(self.datadir + os.sep + name, 'config', inittxt=fleetbotconfigtxt)
            cfg.save()

        # create bot based on type 
        if cfg['type'] == 'irc':
            from gozerbot.irc.bot import Bot
            bot = Bot(cfg)
        elif cfg['type'] == 'jabber':
            from gozerbot.jabber.jabberbot import Jabberbot
            bot = Jabberbot(cfg)
        else:
            logging.debug('unproper type: %s' % cfg['type'])

        # set bot name and initialize bot
        if bot:
            cfg['name'] = bot.name = name
            self.initbot(bot)
            return bot

        # failed to created the bot
        raise Exception("can't make %s bot" % name)

    def resumebot(self, botname, data={}, printto=None):

        """ resume individual bot. """

        # see if we need to exit the old bot
        oldbot = self.byname(botname)
        if oldbot:
            oldbot.exit()

        # recreate config file of the bot
        cfg = Config(datadir + os.sep + 'fleet' + os.sep + botname, 'config')

        # make the bot and resume (IRC) or reconnect (Jabber)
        bot = self.makebot(botname, cfg)
        if bot:
            if oldbot:
                self.replace(oldbot, bot)
            else:
                self.bots.append(bot)
            if not bot.jabber:
                bot._resume(data, printto)
            else:
                start_new_thread(bot.connectwithjoin, ())

    def start(self, botlist=[], enable=False):

        """ startup the bots. """

        # scan the fleet datadir for bots
        dirs = []
        got = []
        for bot in botlist:
            dirs.append(self.datadir + os.sep + bot)

        if not dirs:
            dirs = glob.glob(self.datadir + os.sep + "*")

        for fleetdir in dirs:

            if fleetdir.endswith('fleet'):
                continue

            rlog(10, 'fleet', 'found bot: ' + fleetdir)
            cfg = Config(fleetdir, 'config')

            if not cfg:
                rlog(10, 'fleet', "can't read %s config file" % fleetdir)
                continue

            name = fleetdir.split(os.sep)[-1]

            if not name:
                rlog(10, 'fleet', "can't read botname from %s config file" % \
fleetdir)
                continue

            if not enable and not cfg['enable']:
                rlog(10, 'fleet', '%s bot is disabled' % name)
                continue
            else:
                rlog(10, 'fleet', '%s bot is enabled' % name)

            if not name in fleetdir:
                rlog(10, 'fleet', 'bot name in config file doesnt match dir name')
                continue

            bot = self.makebot(name, cfg)

            if bot:
                start_new_thread(bot.connectwithjoin, ())
                self.addbot(bot)
                got.append(bot)

        return got

        # set startok event
        self.startok.set()

    def save(self):

        """ save fleet data and call save on all the bots. """

        for i in self.bots:
            try:
                i.save()
            except Exception, ex:
                handle_exception()

    def avail(self):

        """ show available fleet bots. """

        return os.listdir(self.datadir)

    def list(self):

        """ return list of bot names. """

        result = []
        for i in self.bots:
            result.append(i.name)
        return result

    def stopall(self):

        """ return bot by name. """

        for i in self.bots:
            try:
                i.stop()
            except:
                pass

    def byname(self, name):

        """ return bot by name. """

        name = name.lower()
        for i in self.bots:
            if name == i.name:
                return i

    def replace(self, name, bot):

        """ replace bot. """

        name = name.lower()
        for i in range(len(self.bots)):
            if name == self.bots[i].name:
                self.bots[i] = bot
                return

    def initbot(self, bot):

        """ initialise a bot. """

        if bot not in self.bots:
            if not os.path.exists(self.datadir + os.sep + bot.name):
                os.mkdir(self.datadir + os.sep + bot.name)
            if type(bot.cfg['owner']) == types.StringType or type(bot.cfg['owner']) == types.UnicodeType:
                bot.cfg['owner'] = [bot.cfg['owner'], ]
                bot.cfg.save()
            users.make_owner(config['owner'] + bot.cfg['owner'])
            rlog(10, 'fleet', 'added bot: ' + bot.name)

    def addbot(self, bot):

        """ add a bot to the fleet .. remove all existing bots with the same name. """

        if bot:
            for i in range(len(self.bots)-1, -1, -1):
                if self.bots[i].name == bot.name:
                    del self.bots[i]
            self.bots.append(bot)

    def connect(self, name):

        """ connect bot to the server. """

        name = name.lower()
        for i in self.bots:
            if i.name == name:
                got = i.connect()
                if got:
                    i.joinchannels()
                    return True
                else:
                    return False

    def delete(self, name):

        """ delete bot with name from fleet. """

        for i in self.bots:
            if i.name == name:
                i.exit()
                self.remove(i)
                i.cfg['enable'] = 0
                i.cfg.save()
                logging.debug('%s disabled' % i.name)
                return 1

    def remove(self, bot):

        """ delete bot by object. """

        self.bots.remove(bot)

    def exit(self, name=None, jabber=False):

        """ call exit on all bots. if jabber=True only jabberbots will exit """

        
        if not name:
            for i in self.bots:
                if jabber and not i.jabber:
                    pass
                else:
                    i.exit()
            return

        name = name.lower()

        for i in self.bots:
            if i.name == name:
                try:
                    i.exit()
                except:
                    handle_exception()
                self.remove(i)
                return 1

    def cmnd(self, event, name, cmnd):
 
        """ do command on a bot by name. """

        name = name.lower()
        bot = self.byname(name)
        if not bot:
            return 0
        from gozerbot.eventbase import EventBase
        j = EventBase(event)
        j.txt = cmnd
        q = Queue.Queue()
        j.queues = [q]
        j.speed = 3
        start_new_thread(plugins.trydispatch, (bot, j))
        result = waitforqueue(q)
        if not result:
            return
        res = ["[%s]" % bot.name, ]
        res += result
        event.reply(res)

    def cmndall(self, event, cmnd):

        """ do a command on all bots. """

        threads = []
        for i in self.bots:
            thread = start_new_thread(self.cmnd, (event, i.name, cmnd))
            threads.append(thread)
        for i in threads:
            i.join(10)

    def broadcast(self, txt):

        """ broadcast txt to all bots. """

        for i in self.bots:
            i.broadcast(txt)

# main fleet object
fleet = Fleet()
