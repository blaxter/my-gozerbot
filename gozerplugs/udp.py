# plugs/udp.py
#
#

"""
the bot has the capability to listen for udp packets which it will use
to /msg a given nick or channel.

1) plugin config
  udp = 1 # set to 1 to enable
  udphost = 'localhost'
  udpport = 5500
  udpallow = ['127.0.0.1', ]
  udpallowednicks = ['#gozerbot', 'dunker']
  udppassword = 'mekker'
  udpseed = "blablablablablaz" # needs to be 16 chars wide

udpallow is set to the ip from which udp packets are accepted .. 
udpallowednicks are nicks/channels the bot is allowed to send messages to
and udppassword is passed along with the message. set udpseed if you want to
have your messages encrypted.

2) limiter

on IRC the bot's /msg to a user/channel are limited to 1 per 3 seconds so the
bot will not excessflood on the server. you can use partyudp if you need no 
delay between sent messages, this will use dcc chat to deliver the message.
on jabber bots there is no delay

3) toudp

::

  # files/toudp.py
  
  use this script to pipeline a programs output to the bot
  
  example: tail -f /var/log/httpd-access.log | ./todup.py
"""


__copyright__ = 'this file is in the public domain'

from gozerbot.fleet import fleet
from gozerbot.generic import rlog, handle_exception, strippedtxt, lockdec
from gozerbot.config import config
from gozerbot.plughelp import plughelp
from gozerbot.partyline import partyline
from gozerbot.threads.thr import start_new_thread
from gozerbot.contrib.rijndael import rijndael
from gozerbot.persist.persistconfig import PersistConfig
import socket, re, time, Queue

plughelp.add('udp' , 'run the udp listen thread')

cfg = PersistConfig()
cfg.define('udp', 0) # set to 1 to enable
cfg.define('udpparty', 0)
cfg.define('udpipv6', 0)
cfg.define('udpmasks', ['192.168*', ])
cfg.define('udphost', "localhost")
cfg.define('udpport', 5500)
cfg.define('udpallow', ["127.0.0.1", ])
cfg.define('udpallowednicks', ["#gozerbot", "dunker"])
cfg.define('udppassword', "mekker", exposed=False)
cfg.define('udpseed', "blablablablablaz", exposed=False) # needs to be 16 chars wide
cfg.define('udpstrip', 1) # strip all chars < char(32)
cfg.define('udpsleep', 0) # sleep in sendloop .. can be used to delay pack
cfg.define('udpdblog', 0)
cfg.define('udpbot', 'default')

def _inmask(addr):
    """ check if addr matches a mask """
    if not cfg['udpmasks']:
        return False
    for i in cfg['udpmasks']:
        i = i.replace('*', '.*')
        if re.match(i, addr):
            return True

class Udplistener(object):
    """ listen for udp messages """

    def __init__(self):
        self.outqueue = Queue.Queue()
        self.queue = Queue.Queue()
        self.stop = 0
        if cfg['udpipv6']:
            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except:
            pass
        self.sock.setblocking(1)
        self.sock.settimeout(1)
        self.loggers = []

    def _outloop(self):
        rlog(5, 'udp', 'starting outloop')
        while not self.stop:
            (printto, txt) = self.outqueue.get()
            if self.stop:
                return
            self.dosay(printto, txt)
        rlog(5, 'udp', 'stopping outloop')

    def _handleloop(self):
        while not self.stop:
            (input, addr) = self.queue.get()
            if not input or not addr:
                continue
            if self.stop:
                break                
            self._handle(input, addr)
            if cfg['udpsleep']:
                time.sleep(cfg['udpsleep'] or 0.001)
        rlog(5, 'udp', 'shutting down udplistener')

    def _listen(self):
        """ listen for udp messages .. /msg via bot"""
        if not cfg['udp']:
            return
        try:
            fleet.startok.wait()
            bot = fleet.byname(cfg['udpbot'] or 'default')
            if not bot:
                rlog(10, 'udp', "can't find %s bot .. not starting" % cfg['udpbot'])
                return
            self.sock.bind((cfg['udphost'], cfg['udpport']))
            rlog(10, 'udp', 'udp listening on %s %s' % (cfg['udphost'], \
cfg['udpport']))
            self.stop = 0
        except IOError:
            handle_exception()
            self.sock = None
            self.stop = 1
            return
        # loop on listening udp socket
        bot.connectok.wait()
        while not self.stop:
            try:
                input, addr = self.sock.recvfrom(64000)
            except socket.timeout:
                continue
            except Exception, ex:
                try:
                    (errno, errstr) = ex
                except ValueError:
                    errno = 0
                    errstr = str(ex)
                if errno == 4:
                    rlog(10, self.name, str(ex))
                    break
                if errno == 35:
                    continue
                else:
                    handle_exception()
                    break
            if self.stop:
                break
            self.queue.put((input, addr))
        rlog(5, 'udp', 'shutting down main loop')

    def _handle(self, input, addr):
        if cfg['udpseed']:
            data = ""
            for i in range(len(input)/16):
                try:
                    data += crypt.decrypt(input[i*16:i*16+16])
                except Exception, ex:
                    rlog(10, 'udp', "can't decrypt: %s" % str(ex))
                    data = input
                    break
        else:
            data = input
        if cfg['udpstrip']:
            data = strippedtxt(data)
        # check if udp is enabled and source ip is in udpallow list
        if cfg['udp'] and (addr[0] in cfg['udpallow'] or \
_inmask(addr[0])):
            # get printto and passwd data
            header = re.search('(\S+) (\S+) (.*)', data)
            if header:
                # check password
                if header.group(1) == cfg['udppassword']:
                    printto = header.group(2)    # is the nick/channel
                    # check if printto is in allowednicks
                    if not printto in cfg['udpallowednicks']:
                        rlog(10, 'udp', "udp denied %s" % printto )
                        return
                    rlog(0, 'udp', str(addr[0]) +  " udp allowed")
                    text = header.group(3)    # is the text
                    self.say(printto, text)
                else:
                    rlog(10, 'udp', "can't match udppasswd from " + \
str(addr))
            else:
                rlog(10, 'udp', "can't match udp from " + str(addr[0]))
        else:
            rlog(10, 'udp', 'denied udp from ' + str(addr[0]))

    def say(self, printto, txt):
        self.outqueue.put((printto, txt))

    def dosay(self, printto, txt):
        if cfg['udpparty'] and partyline.is_on(printto):
            partyline.say_nick(printto, txt)
            return
        bot = fleet.byname(cfg['udpbot'])
        if not bot.jabber and not cfg['nolimiter']:
            time.sleep(3)
        bot.say(printto, txt)
        for i in self.loggers:
            i.log(printto, txt)

if cfg['udp']:
    udplistener = Udplistener()

if cfg['udp'] and cfg['udpseed']:
    crypt = rijndael(cfg['udpseed'])

def init():
    """ init the plugin """
    if cfg['udp']:
        start_new_thread(udplistener._listen, ())
        start_new_thread(udplistener._handleloop, ())
        start_new_thread(udplistener._outloop, ())
    return 1
    
def shutdown():
    """ shutdown the plugin """
    if cfg['udp']:
        udplistener.stop = 1
        udplistener.outqueue.put_nowait((None, None))
        udplistener.queue.put_nowait((None, None))
    return 1

if cfg['udp'] and cfg['udpdblog']:

    from gozerbot.database.db import db

    class Udpdblog:

        """ log udp data to database """

        # see tables/udplog for table definition and add udpdblog = 1 to 
        # the config file

        def log(self, printto, txt):
            """ do the actual logging """
            try:
                res = db.execute("""INSERT into udplog(time,printto,txt)
values(%s,%s,%s) """, (time.time(), printto, txt))
            except Exception, ex:
                rlog(10, 'udp', 'failed to log to db: %s' % str(ex))
            return res

    udplistener.loggers.append(Udpdblog())
    rlog(10, 'udp', 'registered database udp logger')
