# gozerbot/persist.py
#
#

""" allow data to be written to disk in JSON format. creating the persisted 
    object restores data.
"""

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from gozerbot.stats import stats
from gozerbot.generic import rlog
from gozerbot.utils.trace import calledfrom
from gozerbot.utils.lazydict import LazyDict
from gozerbot.datadir import datadir
from simplejson import load, dump

# basic imports
import pickle, thread, os, copy, sys

saving = []
stopsave = 0


class Persist(object):

    """ persist data attribute to JSON file. """

    def __init__(self, filename, default=None, init=True):

        """ Persist constructor """

        self.fn = filename # filename to save to
        self.lock = thread.allocate_lock() # lock used when saving)
        self.data = None # attribute to hold the data

        if init:
            self.init(default)

    def init(self, default=None):

        """ initialize the data. """

        rlog(0, 'persist', 'reading %s' % self.fn)

        # see if file exists .. if not initialize data to default
        try:
            datafile = open(self.fn, 'r')
        except IOError, ex:
            if not 'No such file' in str(ex):
                rlog(10, 'persist', 'failed to read %s: %s' % (self.fn, str(ex)))
            if default != None:
                self.data = copy.deepcopy(default)
            return

        # load the JSON data into attribute
        try:
            self.data = load(datafile)
            datafile.close()
            stats.up('persist', 'load') 
        except Exception, ex:
            rlog(100, 'persist', 'ERROR: %s' % self.fn)
            raise

    def save(self):

        """ persist data attribute. """

        if stopsave:
            rlog(100, 'persist', 'stopping mode .. not saving %s' % self.fn)
            return

        # save data
        try:
            saving.append(str(self.fn))
            self.lock.acquire()
            tmp = self.fn + '.tmp' # tmp file to save to

            # first save to temp file and when done rename
            try:
                datafile = open(tmp, 'w')
            except IOError, ex:
                rlog(100, 'persist', "can't save %s: %s" % (self.fn, str(ex)))
                return

            # dump JSON to file
            dump(self.data, datafile)
            datafile.close()
            os.rename(tmp, self.fn)
            stats.up('persist', 'saved')
            rlog(10, 'persist', '%s saved' % self.fn)

        finally:
            saving.remove(self.fn)
            self.lock.release()


class PlugPersist(Persist):

    """ persist plug related data. """

    def __init__(self, filename, default=None):

        # retrieve plugname where object is constructed
        plugname = calledfrom(sys._getframe())

        # call base constructor with appropiate filename
        Persist.__init__(self, datadir + os.sep + 'plugs' + os.sep + plugname \
+ os.sep + filename, default)


class LazyDictPersist(Persist):

    """ persisted lazy dict. """

    def __init__(self, default={}):

        # called parent constructor
        Persist.__init__(self)

        # if data not initialised set it to a LazyDict
        if not self.data:
            self.data = LazyDict(default)
