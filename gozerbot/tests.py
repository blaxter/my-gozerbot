# gozerbot/tests.py
#
#

""" gozerbot tests framework. """

# gozerbot imports
from config import config
from utils.locking import lockdec
from utils.log import rlog
from utils.trace import calledfrom, whichmodule

# basic imports
import sys, re, thread, copy, time

# used to copy attributes
cpy = copy.deepcopy

# locks
testlock = thread.allocate_lock()
locked = lockdec(testlock)

class Test(object):

    """ a test object. """

    def __init__(self, execstring, expect="", descr="", where="", fakein=""):
        self.plugin = calledfrom(sys._getframe(2))
        self.descr = cpy(descr)
        self.execstring = cpy(execstring)
        self.expect = cpy(expect)
        self.error = ""
        self.groups = []
        self.prev = None
        self.where = cpy(where)
        self.fakein = cpy(fakein)

    @locked
    def run(self, bot, event):

        """ run the test on bot with event. """

        if config['loadlist'] and self.plugin not in config['loadlist']:
            return
        bot.userhosts['bottest'] = 'bottest@test'
        bot.userhosts['mtest'] = 'mekker@test'
        self.error = ""
        self.response = ""
        self.groups = []
        origexec = self.execstring
        origexpect = self.expect

        if self.fakein:
            bot.fakein(self.fakein)
            return self

        if self.prev and self.prev.groups:
            try:
                execstring = self.execstring % self.prev.groups
                self.execstring = execstring
            except TypeError:
                pass
            try:
                expect = self.expect % self.prev.groups
                self.expect = expect
            except TypeError:
                pass

        self.execstring = self.execstring.replace('{{ me }}', event.nick)
        event.txt = event.origtxt = str(self.execstring)
        from gozerbot.plugins import plugins
        self.response = plugins.cmnd(bot, event)

        if self.response and self.expect:
            self.expect = self.expect.replace('{{ me }}', event.nick)
            regex = re.compile(self.expect)
            result = regex.search(str(self.response))
            if not result:
                self.error = 'invalid response'
            else:
                self.groups = result.groups() or self.prev and self.prev.groups

        self.execstring = origexec
        self.expect = origexpect
        return self

class Tests(object):

    """ collection of all tests. """

    def __init__(self):
        self.tests = []
        self.prev = None

    @locked
    def add(self, execstr, expect=None, descr="", fakein=""):

        """ add a test. """

        where = whichmodule(2)
        test = Test(execstr, expect, descr, where, fakein)
        test.prev = self.prev
        self.prev = test
        self.tests.append(test)
        return self

    @locked
    def fakein(self, execstr, expect=None, descr=""):

        """ call bot.fakein(). """ 

        where = whichmodule(2)
        test = Test(execstr, expect, descr, where, execstr)
        test.prev = self.prev
        self.prev = test
        self.tests.append(test)
        return self

    def start(self, func=None):

        """ optional start function. """

        func and func()
        return self

    def end(self, func=None):

        """ optional end function. """

        func and func()
        return self

    def unload(self, plugname):

        """ unload tests. """

        for i in range(len(self.tests)-1, -1, -1):
            if self.tests[i].plugin == plugname:
                del self.tests[i]

    def dotests(self, bot, event):

        """ fire all tests. """

        for test in self.tests:
            test.run(bot, event)

    def sleep(self, seconds):

        """ sleep nr of seconds. """

        time.sleep(seconds)
        return self

# the tests
tests = Tests()
