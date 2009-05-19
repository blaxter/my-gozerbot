# plugs/lag.py
#
# (c) Wijnand 'tehmaze' Modderman - http://tehmaze.com
# BSD License

""" gozerbot lag meter """

from gozerbot.callbacks import callbacks
from gozerbot.commands import cmnds
from gozerbot.examples import examples 
from gozerbot.fleet import fleet
from gozerbot.periodical import interval, periodical
from gozerbot.plughelp import plughelp
import time

plughelp.add('lag', 'lag measuring')

lag_wait = 300

class Lagmeter:

    """ lag meter class """

    def __init__(self):
        self.names = []
        self.sent  = {}
        self.lag   = {}
        self.run   = True

    def update_names(self):
        """ grab all names from irc bots in the fleet """ 
        self.names = [bot.name for bot in fleet.bots if bot.type == 'irc']

    def getlag(self, name):
        """ get lag of <botname> """
        if self.lag.has_key(name):
            return self.lag[name]
        else:
            return False

    def measure(self, name):
        """ measure lag of <botname> """
        bot = fleet.byname(name)
        if not bot:
            return
        if bot.connectok.isSet() and bot.connectok:
            bot.sendraw('PING :LAG %f' % time.time())

    def recieved(self, name, sent):
        """ function called on received PONG """
        self.lag[name] = time.time() - sent

    @interval(lag_wait)
    def loop(self):
        """ lag meter loop """
        fleet.startok.wait()
        self.update_names()
        for name in self.names:
            self.measure(name)

lagmeters = Lagmeter()

def init():
    """ start the lag meter loop """
    lagmeters.loop()
    return 1

def shutdown():
    """ kill all lag meter periodical jobs """ 
    periodical.kill()

def handle_lag(bot, ievent): 
    """ show lag of bot the command is given on """
    lag = lagmeters.getlag(bot.name)
    if lag == False:
        ievent.reply('no lag metered')
    else:
        ievent.reply('lag is %f seconds' % lag)

def connectedcb(bot, ievent):
    """ callback to be called when bot is connected """
    lagmeters.update_names()
    lagmeters.measure(bot.name)

def pongcb(bot, ievent):
    """ PONG callback """
    if len(ievent.arguments) == 3:
        if ievent.arguments[1].lstrip(':') == 'LAG':
            try:
                sent = float(ievent.arguments[2])
                lagmeters.recieved(bot.name, sent) 
            except ValueError:
                pass

cmnds.add('lag', handle_lag, ['USER'])
examples.add('lag', 'shows the current lag', 'lag')
callbacks.add('001', connectedcb)
callbacks.add('PONG', pongcb)
