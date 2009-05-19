# gozerbot/lockmanager.py
#
#

""" manages locks """

__copyright__ = 'this file is in the public domain'

from log import rlog
import thread

class Lockmanager(object):

    """ place to hold locks """

    def __init__(self):
        self.locks = {}

    def allocate(self, name):
        """ allocate a new lock """
        name = name.lower()
        self.locks[name] = thread.allocate_lock()
        rlog(10, 'lockmanager', 'allocated %s' % name)
        
    def get(self, name):
        """ get lock """
        name = name.lower()
        if not self.locks.has_key(name):
            self.allocate(name)
        return self.locks[name]
        
    def delete(self, name):
        """ delete lock """
        if self.locks.has_key(name):
            del self.locks[name]

    def acquire(self, name):
        """ acquire lock """
        name = name.lower()
        if not self.locks.has_key(name):
            self.allocate(name)
        rlog(10, 'lockmanager', 'acquire %s' % name)
        self.locks[name].acquire()

    def release(self, name):
        """ release lock """
        name = name.lower()
        rlog(10, 'lockmanager', 'releasing %s' % name)
        self.locks[name].release()

lockmanager = Lockmanager()
