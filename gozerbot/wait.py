# gozerbot/wait.py
#
#

""" wait for ircevent based on ircevent.CMND """

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from generic import rlog, lockdec
import threads.thr as thr

# basic imports
import time, thread

# locks
waitlock = thread.allocate_lock()
locked = lockdec(waitlock)

class Wait(object):

    """ lists of ircevents to wait for """

    def __init__(self):
        self.waitlist = []
        self.ticket = 0

    def register(self, cmnd, catch, queue, timeout=15):

        """ register wait for cmnd. """

        rlog(1, 'wait', 'registering for cmnd ' + cmnd)
        self.ticket += 1
        self.waitlist.insert(0, (cmnd, catch, queue, self.ticket))
        if timeout:
            # start timeout thread
            thr.start_new_thread(self.dotimeout, (timeout, self.ticket))
        return self.ticket

    def check(self, ievent):

        """ check if there are wait items for ievent .. check if 'catch' 
            matches on ievent.postfix if so put ievent on queue. """

        cmnd = ievent.cmnd
        for item in self.waitlist:
            if item[0] == cmnd:
                if cmnd == "JOIN":
	            catch = ievent.txt + ievent.postfix
                else:
                    catch = ievent.nick + ievent.postfix
                if item[1] in catch:
                    ievent.ticket = item[3]
                    item[2].put_nowait(ievent)
                    self.delete(ievent.ticket)
                    rlog(1, 'wait', 'got response for %s' % item[0])
                    ievent.isresponse = True

    def dotimeout(self, timeout, ticket):

        """ start timeout thread for wait with ticket nr. """

        rlog(1, 'wait', 'starting timeouthread for %s' % str(ticket))
        time.sleep(float(timeout))
        self.delete(ticket)

    @locked
    def delete(self, ticket):

        """ delete wait item with ticket nr. """

        for itemnr in range(len(self.waitlist)-1, -1, -1):
            if self.waitlist[itemnr][3] == ticket:
                self.waitlist[itemnr][2].put_nowait(None)
                del self.waitlist[itemnr]
                rlog(1, 'wait', 'deleted ' + str(ticket))
                return 1

class Privwait(Wait):

    """ wait for privmsg .. catch is on nick """

    def register(self, catch, queue, timeout=15):

        """ register wait for privmsg. """

        rlog(1, 'privwait', 'registering for ' + catch)
        return Wait.register(self, 'PRIVMSG', catch, queue, timeout)

    def check(self, ievent):

        """ check if there are wait items for ievent. """

        for item in self.waitlist:
            if item[0] == 'PRIVMSG':
                if ievent.userhost == item[1]:
                    ievent.ticket = item[3]
                    item[2].put_nowait(ievent)
                    self.delete(ievent.ticket)
                    rlog(1, 'privwait', 'got response for %s' % item[0])
                    ievent.isresponse = True

class Jabberwait(Wait):

    """ wait object for jabber messages. """

    def register(self, catch, queue, timeout=15):

        """ register wait for privmsg. """

        rlog(1, 'jabberwait', 'registering for %s' % catch)
        self.ticket += 1
        self.waitlist.append((catch, queue, self.ticket))
        if timeout:
            thr.start_new_thread(self.dotimeout, (timeout, self.ticket))
        return self.ticket

    def check(self, msg):

        """ check if <msg> is waited for. """

        for teller in range(len(self.waitlist)-1, -1, -1):
            i = self.waitlist[teller]
            if i[0] == msg.userhost:
                msg.ticket = i[2]
                i[1].put_nowait(msg)
                self.delete(msg.ticket)
                rlog(10, 'jabberwait', 'got response for %s' % i[0])
                msg.isresponse = 1

    @locked
    def delete(self, ticket):

        """ delete wait item with ticket nr. """

        for itemnr in range(len(self.waitlist)-1, -1, -1):
            item = self.waitlist[itemnr]
            if item[2] == ticket:
                item[1].put_nowait(None)
                try:
                    del self.waitlist[itemnr]
                    rlog(1, 'jabberwait', 'deleted ' + str(ticket))
                except IndexError:
                    pass
                return 1

class Jabbererrorwait(Jabberwait):

    """ wait for jabber errors. """

    def check(self, msg):

        """ check if <msg> is waited for. """

        if not msg.getType() == 'error':
            return

        errorcode = msg.getErrorCode()

        for teller in range(len(self.waitlist)-1, -1, -1):
            i = self.waitlist[teller]
            if i[0] == 'ALL' or i[0] == errorcode:
                msg.error = msg.getError()
                msg.ticket = i[2]
                i[1].put_nowait(msg)
                self.delete(msg.ticket)
                rlog(10,'jabbererrorwait','got error response for %s' % i[0])
