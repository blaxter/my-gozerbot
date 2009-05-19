# gozerbot/redispatcher.py
#
#

""" implement RE (regular expression) dispatcher. """

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from config import config
from generic import rlog, calledfrom, handle_exception, lockdec
from runner import cmndrunners
import threads.thr as thr

# basic imports
import sys, re, copy, types, thread

# locks
relock = thread.allocate_lock()
locked = lockdec(relock)

class Recallback(object):

    """ a regular expression callback """

    def __init__(self, index, regex, func, perm, plugname, speed=5, \
threaded=True, allowqueue=True, options={}):
        self.name = thr.getname(func) # name of the callback
        self.index = index # index into the list
        self.regex = regex # the RE to match
        self.compiled = re.compile(regex) # compiled RE
        self.func = func # the function to call if RE matches
        # make sure perms is a list
        if type(perm) == types.ListType:
            self.perms = list(perm)
        else:
            self.perms = [perm, ]
        # plug name
        self.plugname = plugname # plugname where RE callbacks is registered
        self.speed = copy.deepcopy(speed) # speed at which the function runs
        self.threaded = copy.deepcopy(threaded) # set when run threaade
        self.allowqueue = copy.deepcopy(allowqueue) # set when pipeline is allowed
        self.options = dict(options) # options set on the callback

class Redispatcher(object):

    """ this is were the regexs callbacks live. """

    def __init__(self):
        self.relist = []
        
    def size(self):

        """ nr of callbacks. """

        return len(self.relist)

    def whatperms(self):

        """ return possible permissions. """

        result = []
        for i in self.relist:
            for j in i.perms:
                if j not in result:
                    result.append(j)
        return result

    def list(self, perm):

        """ list re with permission perm. """

        result = []
        perm = perm.upper()
        for recom in self.relist:
            if perm in recom.perms:
                result.append(recom)
        return result

    def getfuncnames(self, plug):

        """ return function names in plugin. """

        result = []
        for i in self.relist:
            if i.plugname == plug:
                result.append(i.func.func_name)
        return result
        
    def permoverload(self, funcname, perms):

        """ overload permission of function with funcname.  """

        perms = [perm.upper() for perm in perms]
        got = 0
        for nr in range(len(self.relist)):
            try:
                if self.relist[nr].func.func_name == funcname:
                    self.relist[nr].perms = list(perms)
                    rlog(0, 'redispatcher', '%s function overloaded with %s' \
% (funcname, perms))
                    got = 1
            except AttributeError:
                rlog(10, 'redispatcher', 'permoverload: no %s function' % \
funcname)
        if got:
            return 1

    def add(self, index, regex, func, perm, speed=5, threaded=True, allowqueue=True, options={}):

        """ add a command. """

        try:
            # get plugin name from where callback is added
            plugname = calledfrom(sys._getframe())
            if config['loadlist'] and plugname not in config['loadlist']:
                return
            # add Recallback
            self.relist.append(Recallback(index, regex, func, perm, plugname, \
speed, threaded, allowqueue, options))
            # sort of index number
            self.relist.sort(lambda a, b: cmp(a.index, b.index))
            rlog(0, 'redispatcher', 'added %s (%s) ' % (regex, plugname))
        finally:
            pass

    def unload(self, plugname):

        """ unload regexs commands. """

        got = 0
        try:
            for i in range(len(self.relist)-1, -1 , -1):
                if self.relist[i].plugname == plugname:
                    rlog(1, 'redispatcher', 'unloading %s (%s)' % \
(self.relist[i].regex, plugname))
                    del self.relist[i]
                    got = 1
        finally:    
            pass
        if got:
            return 1

    def getcallback(self, txt):

        """ get re callback if txt matches. """

        for i in self.relist:
            try:
                result = re.search(i.compiled, txt)
                if result:
                    return i
            except:
                pass

    def dispatch(self, callback, txt):

        """ dispatch callback on txt. """

        try:
            result = re.search(callback.compiled, txt)
            if result:
                if callback.threaded:
                    thr.start_new_thread(callback.func, (txt, result.groups()))
                else:
                    cmndrunners.put(callback.plugname, callback.func, txt, \
result.groups())
                    return 1
        except Exception, ex:
            handle_exception()

class Botredispatcher(Redispatcher):

    """ dispatcher on ircevent. """

    def dispatch(self, callback, bot, ievent):

        """ dispatch callback on ircevent. """

        try:
            result = re.search(callback.compiled, ievent.txt.strip())
            if result:
                ievent.groups = list(result.groups())                
                if callback.threaded:
                    thr.start_bot_command(callback.func, (bot, ievent))
                else:
                    cmndrunners.put(callback.plugname, callback.func, bot, \
ievent)
                return 1
        except Exception, ex:
            handle_exception(ievent)

# dispatcher before commands are checked
rebefore = Botredispatcher()

# dispatcher after commands are checked
reafter = Botredispatcher()
