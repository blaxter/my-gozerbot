# gozerbot/persist.py
#
#

""" allow data to be pickled to disk .. creating the persisted object
    restores data
"""

__copyright__ = 'this file is in the public domain'

from gozerbot.generic import rlog
import cPickle, thread, os, copy

saving = []
stopsave = 0

class Persist(object):

    """ persist data attribute to pickle file """

    def __init__(self, filename, default=None):
        rlog(1, 'compat-persist', 'reading %s' % filename)
        self.fn = filename
        self.lock = thread.allocate_lock()
        self.data = None
        # load data from pickled file
        try:
            datafile = open(filename, 'r')
        except IOError:
            if default != None:
                self.data = copy.deepcopy(default)
            return
        try:
            self.data = cPickle.load(datafile)
            datafile.close()
        except:
            if default != None:
                self.data = copy.deepcopy(default)
            else:
                rlog(100, 'compat-persist', 'ERROR: %s' % filename)
                raise

    def save(self):
        """ save persist data """
        if stopsave:
            rlog(100, 'compat-persist', 'stopping mode .. not saving %s' % self.fn)
            return
        try:
            saving.append(str(self.fn))
            self.lock.acquire()
            # first save to temp file and when done rename
            tmp = self.fn + '.tmp'
            try:
                datafile = open(tmp, 'w')
            except IOError:
                rlog(100, 'compat-persist', "can't save %s" % self.fn)
                return
            cPickle.dump(self.data, datafile)
            datafile.close()
            os.rename(tmp, self.fn)
            rlog(10, 'compat-persist', '%s saved' % self.fn)
        finally:
            saving.remove(self.fn)
            self.lock.release()
