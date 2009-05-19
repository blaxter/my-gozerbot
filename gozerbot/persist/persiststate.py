# gozerbot/persiststate.py
#
#

""" persistent state classes """

__copyright__ = 'this file is in the public domain'

from gozerbot.generic import calledfrom, rlog
from gozerbot.datadir import datadir
from persist import Persist
import types, os, sys

class PersistState(Persist):

    """ base persitent state class """

    def __init__(self, filename):
        Persist.__init__(self, filename, {})
        self.types = dict((i, type(j)) for i, j in self.data.iteritems())

    def __getitem__(self, key):

        """ get state item. """

        return self.data[key]

    def __setitem__(self, key, value):

        """ set state item. """

        self.data[key] = value

    def define(self, key, value):

        """ define a state item. """

        if not self.data.has_key(key) or type(value) != self.types[key]:
            if type(value) == types.StringType:
                value = unicode(value)
            if type(value) == types.IntType:
                value = long(value)
            self.data[key] = value

class PlugState(PersistState):

    """ state for plugins. """

    def __init__(self):
        self.plugname = calledfrom(sys._getframe())
        rlog(10, 'persiststate', 'iniitialising %s' % self.plugname)
        PersistState.__init__(self, datadir + os.sep + 'plugs' + os.sep + self.plugname + os.sep + 'state')

class ObjectState(PersistState):

    """ state for usage in constructors. """

    def __init__(self):
        PersistState.__init__(self, datadir + os.sep + calledfrom(sys._getframe(1))+'.state')

class UserState(PersistState):

    """ state for users. """

    def __init__(self, username):
        self.datadir = datadir + os.sep + 'users' + os.sep + username
        PersistState.__init__(self, self.datadir + os.sep + 'state')
