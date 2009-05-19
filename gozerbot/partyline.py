# gozerbot/partyline.py
#
#

""" provide partyline functionality .. manage dcc sockets. """


__copyright__ = 'this file is in the public domain'
__credits__ = 'Aim'

# gozerbot imports
from generic import rlog, handle_exception
from fleet import fleet
from simplejson import load
from threads.thr import start_new_thread

# basic imports
import thread, pickle, socket

class Partyline(object):

    """ partyline can be used to talk through dcc chat connections. """

    def __init__(self):
        self.socks = [] # partyline sockets list
        self.lock = thread.allocate_lock()

    def _doresume(self, data, reto=None):

        """ resume a party line connection after reboot. """

        for i in data['partyline']:
            bot = fleet.byname(i['botname'])
            sock = socket.fromfd(i['fileno'], socket.AF_INET, socket.SOCK_STREAM)
            sock.setblocking(1)
            nick = i['nick']
            userhost = i['userhost']
            channel = i['channel']

            if not bot:
                rlog(10, 'partyline', "can't find %s bot in fleet" % i['botname'])
                continue

            self.socks.append({'bot': bot, 'sock': sock, 'nick': nick, 'userhost': userhost, 'channel': channel, 'silent': i['silent']})
            bot._dccresume(sock, nick, userhost, channel)        

            if reto:
                self.say_nick(nick, 'rebooting done')

    def _resumedata(self):

        """ return data used for resume. """

        result = []
        for i in self.socks:
            result.append({'botname': i['bot'].name, 'fileno': i['sock'].fileno(), 'nick': i['nick'], 'userhost': i['userhost'], 'channel': i['channel'], 'silent': i['silent']})

        return result

    def resume(self, sessionfile):

        """ resume from session file. """

        session = load(open(sessionfile))
        try:
            reto = session['channel']
            self._doresume(session, reto)
        except Exception, ex:
            handle_exception()

    def stop(self, bot):

        """ stop all user on bot. """

        for i in self.socks:
            if i['bot'] == bot:
                try:
                    i['sock'].shutdown(2)
                    i['sock'].close()
                except:
                    pass

    def stop_all(self):

        """ stop every users on partyline. """

        for i in self.socks:
            try:
                i['sock'].shutdown(2)
                i['sock'].close()
            except:
                pass

    def loud(self, nick): 

        """ enable broadcasting of txt for nick. """

        for i in self.socks:
            if i['nick'] == nick:
                i['silent'] = False

    def silent(self, nick):

        """ disable broadcasting txt from/to nick. """

        for i in self.socks:
            if i['nick'] == nick:
                i['silent'] = True

    def add_party(self, bot, sock, nick, userhost, channel):

        ''' add a socket with nick to the list. '''

        for i in self.socks:
            if i['sock'] == sock:
                return            

        self.socks.append({'bot': bot, 'sock': sock, 'nick': nick, \
'userhost': userhost, 'channel': channel, 'silent': False})
        rlog(1, 'partyline', 'added user %s on the partyline' % nick)

    def del_party(self, nick):

        ''' remove a socket with nick from the list. '''

        nick = nick.lower()
        self.lock.acquire()

        try:
            for socknr in range(len(self.socks)-1, -1, -1):	
                if self.socks[socknr]['nick'].lower() == nick:
                    del self.socks[socknr]
            rlog(1, 'partyline', 'removed user %s from the partyline' % nick)
        finally:
            self.lock.release()

    def list_nicks(self):

        ''' list all connected nicks. '''

        result = []
        for item in self.socks:
            result.append(item['nick'])
        return result

    def say_broadcast(self, txt):

        ''' broadcast a message to all ppl on partyline. '''

        for item in self.socks:
            if not item['silent']:
                item['sock'].send("%s\n" % txt)

    def say_broadcast_notself(self, nick, txt):

        ''' broadcast a message to all ppl on partyline. '''

        nick = nick.lower()
        for item in self.socks:
            if item['nick'] == nick:
                continue
            if not item['silent']:
                item['sock'].send("%s\n" % txt)

    def say_nick(self, nickto, msg):

        ''' say a message on the partyline to an user. '''

        nickto = nickto.lower()
        for item in self.socks:
            if item['nick'].lower() == nickto:
                if not '\n' in msg:
                    msg += "\n"
                item['sock'].send("%s" % msg)
                return

    def is_on(self, nick):

        ''' checks if user an is on the partyline. '''

        nick = nick.lower()
        print nick
        for item in self.socks:
            if item['nick'].lower() == nick:
                print 'got'
                return 1
        return 0

# the partyline !
partyline = Partyline()
