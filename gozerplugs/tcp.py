# plugs/tcp.py
#
#

""" allow incoming tcp connection for messaging """

__copyright__ = 'this file is in the public domain'

from gozerbot.fleet import fleet
from gozerbot.generic import rlog, handle_exception, strippedtxt, lockdec
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.config import config
from gozerbot.plughelp import plughelp
from gozerbot.partyline import partyline
from gozerbot.threads.thr import start_new_thread
from gozerbot.contrib.rijndael import rijndael
import socket, re, time, Queue

plughelp.add('tcp' , 'run the tcp listen thread')

cfg = PersistConfig()
cfg.define('tcp', 0) # set to 1 to enable
cfg.define('tcpparty', 0)
cfg.define('tcpipv6', 0)
cfg.define('tcpmasks', ['192.168*', ]) 
cfg.define('tcphost', "localhost")
cfg.define('tcpport', 5500)
cfg.define('tcpallow', ["127.0.0.1", ])
cfg.define('tcpallowednicks', ["#gozerbot", "dunker"])
cfg.define('tcppassword', "mekker", exposed=False)
cfg.define('tcpseed', "blablablablablaz", exposed=False) # needs to be 16 chars
cfg.define('tcpstrip', 1) # strip all chars < char(32)
cfg.define('tcpsleep', 0) # sleep in sendloop .. can be used to delay packet traffic
cfg.define('tdpdblog', 0)
cfg.define('tcpbot', 'default')

def _inmask(addr):
    """ check if addr matches a mask """
    if not cfg['tcpmasks']:
        return False
    for i in cfg['tcpmasks']:
        i = i.replace('*', '.*')
        if re.match(i, addr):
            return True

class Tcplistener(object):
    """ listen for tcp messages """

    def __init__(self):
        self.outqueue = Queue.Queue()
        self.queue = Queue.Queue()
        self.stop = 0
        if cfg['tcpipv6']:
            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except:
            pass
        self.sock.setblocking(1)
        self.sock.settimeout(1)
        self.loggers = []

    def _outloop(self):
        rlog(5, 'tcp', 'starting outloop')
        while not self.stop:
            (printto, txt) = self.outqueue.get()
            if self.stop:
                return
            self.dosay(printto, txt)
        rlog(5, 'tcp', 'stopping outloop')

    def _handleloop(self):
        while not self.stop:
            (input, addr) = self.queue.get()
            if not input or not addr:
                continue
            if self.stop:
                break                
            self._handle(input, addr)
            if cfg['tcpsleep']:
                time.sleep(cfg['tcpsleep'] or 0.001)
        rlog(5, 'tcp', 'shutting down tcplistener')

    def _listen(self):
        """ listen for tcp messages .. /msg via bot"""
        if not cfg['tcp']:
            return
        try:
            fleet.startok.wait()
            bot = fleet.byname(cfg['tcpbot'] or 'default')
            if not bot:
                rlog(10, 'tcp', "can't find main bot .. not starting")
                return
            # get listen socket on host were running on
            self.sock.bind((cfg['tcphost'], cfg['tcpport']))
            self.sock.listen(1)
            rlog(10, 'tcp', 'tcp listening on %s %s' % (cfg['tcphost'], \
cfg['tcpport']))
            self.stop = 0
        except IOError:
            handle_exception()
            self.sock = None
            self.stop = 1
            return
        # loop on listening tcp socket
        bot.connectok.wait()
        while not self.stop:
            try:
                (sock, addr) = self.sock.accept()
                rlog(10, 'tcp', 'connection from %s' % str(addr))
            except socket.timeout:
                continue
            except Exception, ex:
                if 'Invalid argument' in str(ex):
                    continue
                handle_exception()
                break
            if cfg['tcp'] and (addr[0] in cfg['tcpallow'] or \
_inmask(addr[0])):
                start_new_thread(self.handlesocket, (sock, addr))

    def handlesocket(self, sock, addr):
        while 1:
            time.sleep(0.001)
            try:
                input = sock.recv(4096)
                if not input:
                    return
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
        rlog(5, 'tcp', 'shutting down main loop')

    def _handle(self, input, addr):
        if cfg['tcpseed']:
            data = ""
            for i in range(len(input)/16):
                try:
                    data += crypt.decrypt(input[i*16:i*16+16])
                except Exception, ex:
                    rlog(10, 'tcp', "can't decrypt: %s" % str(ex))
                    data = input
                    break
        else:
            data = input
        if cfg['tcpstrip']:
            data = strippedtxt(data)
        # check if tcp is enabled and source ip is in tcpallow list
        if cfg['tcp'] and (addr[0] in cfg['tcpallow'] or \
_inmask(addr[0])):
            # get printto and passwd data
            header = re.search('(\S+) (\S+) (.*)', data)
            if header:
                # check password
                if header.group(1) == cfg['tcppassword']:
                    printto = header.group(2)    # is the nick/channel
                    # check if printto is in allowednicks
                    if not printto in cfg['tcpallowednicks']:
                        rlog(10, 'tcp', "tcp denied %s" % printto )
                        return
                    rlog(0, 'tcp', str(addr[0]) +  " tcp allowed")
                    text = header.group(3)    # is the text
                    self.say(printto, text)
                else:
                    rlog(10, 'tcp', "can't match tcppasswd from " + \
str(addr))
            else:
                rlog(10, 'tcp', "can't match tcp from " + str(addr[0]))
        else:
            rlog(10, 'tcp', 'denied tcp from ' + str(addr[0]))

    def say(self, printto, txt):
        self.outqueue.put((printto, txt))

    def dosay(self, printto, txt):
        if cfg['tcpparty'] and partyline.is_on(printto):
            partyline.say_nick(printto, txt)
            return
        bot = fleet.getmainbot()
        if not bot.jabber and not bot.cfg['nolimiter']:
            time.sleep(3)
        bot.say(printto, txt)
        for i in self.loggers:
            i.log(printto, txt)

if cfg['tcp']:
    tcplistener = Tcplistener()

if cfg['tcp'] and cfg['tcpseed']:
    crypt = rijndael(cfg['tcpseed'])

def init():
    """ init the plugin """
    if cfg['tcp']:
        start_new_thread(tcplistener._listen, ())
        start_new_thread(tcplistener._handleloop, ())
        start_new_thread(tcplistener._outloop, ())
    return 1
    
def shutdown():
    """ shutdown the plugin """
    if cfg['tcp']:
        tcplistener.sock.close()
        tcplistener.stop = 1
        tcplistener.outqueue.put_nowait((None, None))
        tcplistener.queue.put_nowait((None, None))
        time.sleep(2)
    return 1

if cfg['tcp'] and cfg['tcpdblog']:

    from gozerbot.database.db import db

    class Tcpdblog:

        """ log tcp data to database """

        # see tables/tcplog for table definition and add tcpdblog = 1 to 
        # the config file

        def log(self, printto, txt):
            """ do the actual logging """
            try:
                res = db.execute("""INSERT into tcplog(time,printto,txt)
values(%s,%s,%s) """, (time.time(), printto, txt))
            except Exception, ex:
                rlog(10, 'tcp', 'failed to log to db: %s' % str(ex))
            return res

    tcplistener.loggers.append(Udpdblog())
    rlog(10, 'tcp', 'registered database tcp logger')
