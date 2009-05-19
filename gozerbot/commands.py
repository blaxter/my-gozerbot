# gozerbot/commands.py
#
#

""" implements commands. """

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from gozerbot.stats import stats
from utils.generic import makeoptions
from eventbase import defaultevent
from config import config
from generic import rlog, calledfrom, handle_exception, lockdec
from runner import cmndrunners
from threads.thr import start_new_thread, start_bot_command

# basic imports
import sys, re, copy, types, thread

# lock
commandlock = thread.allocate_lock()
locked = lockdec(commandlock)


class Command(object):

    """ implements a command. """

    def __init__(self, func, perm, plugname, speed=5, threaded=False, allowqueue=True, options={}):

        self.name = str(func) # function name is string representation of the function 
        self.func = func # function to call

        # make sure permission(s) are stored in a list
        if type(perm) == types.ListType:
            self.perms = list(perm)
        else:
            self.perms = [perm, ]

        self.plugname = plugname # plugin name
        self.speed = copy.deepcopy(speed) # speed to execute command with
        self.threaded = copy.deepcopy(threaded) # set if threaded exec is required
        self.allowqueue = copy.deepcopy(allowqueue) # set if command is allowed to be used in pipeline
        self.options = dict(options) # options set in the command 

        
class Commands(dict):

    """ commands object is a dict containing the commands. """

    def __setitem__(self, name, value):

        """ set command. """

        dict.__setitem__(self, name, value)

    def __delitem__(self, name):

        """ delete command. """

        dict.__delitem__(self, name)

    def size(self):

        """ nr of commands. """

        return len(self)

    @locked
    def whatperms(self):

        """ return all possible permissions. """

        result = []

        # loop over the commands and collect all possible permissions
        for i in self.values():
            for j in i.perms:
                if j not in result:
                    result.append(j)

        return result

    @locked
    def list(self, perm):

        """ list commands with permission perm. """

        result = []

        # make sure perm is a list
        if type(perm) != types.ListType:
            perm = perm.upper()
            perms = [perm, ]
        else:
            perms = perm

        # loop over commands collecting all command having permission
        for name, cmnd in self.items():
            for i in perms:
                if i in cmnd.perms:
                    result.append(name)

        return result

    @locked
    def getfuncnames(self, plug):

        """ get all function names of commands in a plugin. """
        result = []

        # collect function names 
        for i in self.values():
            if i.plugname == plug:
                result.append(i.func.func_name)

        return result

    @locked
    def getoptions(self, command):

        """ get options of a command. """

        result = []

        for name, cmnd in self.iteritems():
            if name == command:
                return makeoptions(defaultevent, cmnd.options)

    @locked
    def permoverload(self, name, perms):

        """ overload permission of function with funcname  """

        # make sure all perms are uppercase
        perms = [perm.upper() for perm in perms]

        # overload the command with given permissions
        for cmndname, com in self.iteritems():
            if cmndname == command:
                return com.options

    @locked
    def add(self, cmnd, func, perm, speed=5, threaded=False, allowqueue=True, options={}):

        """ add a command. """

        # plugin where the command is added
        plugname = calledfrom(sys._getframe(1))

        # check if plugin is in loadlist .. if not dont register command. 
        if config['loadlist'] and plugname not in config['loadlist']:
            return

        rlog(-3, 'commands', 'added %s (%s) ' % (cmnd, plugname))

        # add command
        self[cmnd.lower()] = Command(func, perm, plugname, speed, threaded, allowqueue, options)
        self[cmnd.lower()].name = cmnd.lower()

    @locked
    def apropos(self, what, perms=[]):

        """ search for command. """

        result = []

        #  loop over commands collecting all commands that contain given txt
        for name, cmnd in self.iteritems():
            if perms:
                go = False
                for i in perms:
                    if i in cmnd.perms:
                        go = True
                if not go:
                    continue                
            if re.search(what, name):
                result.append(name)

        return result

    @locked
    def unload(self, plugname):

        """ unload plugin commands. """

        results = []

        # look for the commands registerd in plugin
        for name, cmnd in self.iteritems():
            if cmnd.plugname == plugname:
                results.append(name)

        got = 0

        # remove commands
        for name in results:
            del self[name]
            rlog(-3, 'commands', 'unloaded %s (%s)' % (name, plugname))
            got = 1

        if got:
            return 1

    @locked
    def whereis(self, what):

        """ locate plugin a command is registered in. """

        result = []

        # find plugin 
        for name, cmnd in self.iteritems():
            if name == what:
                if not cmnd.plugname in result:
                    result.append(cmnd.plugname)

        return result

    def perms(self, name):

        """ get permission of command. """

        name = name.lower()

        if self.has_key(name):
            return self[name].perms
        else:
            return []

    def setperm(self, name, perm):

        """ set permission of command. """

        name = name.lower()
        perm = perm.upper()

        if self.has_key(name):
            if perm not in self[name].perms:
                self[name].perms.append(perm)
            return 1

    @locked
    def getcommand(self, txt):

        """ return commands matching with txt. """

        textlist = txt.split()

        if not textlist:
            return None

        cmnd = textlist[0].lower()

        if self.has_key(cmnd):
            com = self[cmnd] # the command
            return com
        else:
            return None

    def dispatch(self, com, txt):

        """ dispatch command. """

        if com.threaded:
            start_new_thread(com.func, (txt, ))
        else:
            cmndrunners[10-com.speed].put(com.name, com.func, txt)
        return 1

class Botcommands(Commands):

    """ commands for the IRC bot .. dispatch with (bot, ircevent) """

    def dispatch(self, com, bot, ievent):

        """ dispatch on ircevent passing bot an ievent as arguments """

        if bot.stopped:
            return 0

        # stats
        stats.up('cmnds', com.name)
        stats.up('cmnds', com.plugname)
        stats.up('cmnds', 'speed%s' % com.speed)

        # execute command
        if com.threaded:
            start_bot_command(com.func, (bot, ievent))
        else:	
            speed = ievent.speed or com.speed
            ievent.speed = speed
            cmndrunners[10-speed].put(com.name, com.func, bot, ievent)
        return 1

cmnds = Botcommands()
