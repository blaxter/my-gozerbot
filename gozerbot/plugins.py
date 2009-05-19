# gozerbot/plugins.py
#
#

""" provide plugin infrastructure """

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from gozerbot.stats import stats
from gozerbot.tests import tests
from gozerbot.datadir import datadir
from users import users
from monitor import outmonitor, saymonitor, jabbermonitor
from generic import rlog, handle_exception, checkchan, lockdec, \
plugnames, waitforqueue, uniqlist, makeoptions, makeargrest, cleanpycfile
from gozerimport import gozer_import, force_import
from persist.persist import Persist
from persist.persistconfig import PersistConfig
from config import config
from commands import cmnds
from callbacks import callbacks, jcallbacks
from redispatcher import rebefore, reafter
from irc.ircevent import Ircevent
from aliases import aliascheck
from ignore import shouldignore
from threads.thr import start_new_thread, getname
from persist.persiststate import PersistState
from simplejson import loads
from morphs import inputmorphs, outputmorphs

# basic imports
import os, os.path, thread, time, Queue, re

loadlock = thread.allocate_lock()
loadlocked = lockdec(loadlock)

class Plugins(object):

    """ hold all the plugins. """

    def __init__(self):
        self.plugs = {} # dict with the plugins
        self.reloadlock = thread.allocate_lock()
        # persisted data for deny of plugins (blacklist)
        self.plugdeny = Persist(datadir + os.sep + 'plugdeny', init=False)
        if not self.plugdeny.data:
            self.plugdeny.data = []
        # persisted data for allowing of plugins (whitelist)
        self.plugallow = Persist(datadir + os.sep + 'plugallow', init=False)
        if not self.plugallow.data:
            self.plugallow.data = []
        self.avail = [] # available plugins
        self.ondisk = [] # plugisn available for reload
        self.initcalled = [] # plugins which init functions are called
        self.overloads = {} # plugins to overload
 
    def __getitem__(self, item):

        """ return plugin. """

        if self.plugs.has_key(item):
            return self.plugs[item]
        else:
            return None

    def get(self, item, attr):

        """ get attribute of plugin. """

        if self.plugs.has_key(item):
            return getattr(self.plugs[item], attr)

    def whatperms(self):

        """ return what permissions are possible. """

        result = []

        # search RE callbacks before the commands
        for i in rebefore.whatperms():
            if not i in result:
                result.append(i)

        # search the commands
        for i in cmnds.whatperms():
            if not i in result:
                result.append(i)

        # search RE callbacks after commands
        for i in reafter.whatperms():
            if not i in result:
                result.append(i)

        result.sort()
        return result

    def exist(self, name):

        """ see if plugin <name> exists. """

        if self.plugs.has_key(name):
            return 1 

    def disable(self, name):

        """ prevent plugins <name> to be loaded. """

        try:
            config['loadlist'].remove(name)
            config.save()
            self.plugdeny.data.append(name)
            self.plugdeny.save()
        except:
            pass

    def enable(self, name):

        """ enable plugin <name>. """

        try:
            if name not in config['loadlist']:
                config['loadlist'].append(name)
                config.save()
            self.plugdeny.data.remove(name)
            self.plugdeny.save()
        except:
            pass

    def plugsizes(self):

        """ call the size() function in all plugins. """

        reslist = []
        for i, j in self.plugs.iteritems():
            try:
                reslist.append("%s: %s" % (i, j.size()))
            except AttributeError:
                pass
        return reslist

    def list(self):

        """ list of registered plugins. """

        self.avail.sort()
        return self.avail

    def plugimport(self, mod, name):

        """ import a plugin. """

        if name in config['loadlist']:
            self.reload(mod, name)
        else:
            self.reload(mod, name, enable=False)
        if self.plugs.has_key(name):
            return self.plugs[name]

    def regplugin(self, mod, name):

        """ register plugin. """

        name = name.lower()
        mod = mod.lower()
        modname = mod + '.' + name

        # see if plugin is in deny
        if name in self.avail:
            rlog(9, 'plugins', '%s already registered' % name)
            return
        if name in self.plugdeny.data:
            rlog(10, 'plugins', '%s.%s in deny .. not loading' % \
(mod, name))
            return 0
        if config.has_key('loadlist') and name not in config['loadlist'] and 'gozerplugs' in modname and name not in self.plugallow.data:
                rlog(9, 'plugins', 'not loading %s.%s' % (mod, name))
                return 0

        # if plugin is already registered unload it
        if self.plugs.has_key(name):
            rlog(10, 'plugins', 'overloading %s plugin with %s version' \
% (name, mod))
            self.unloadnosave(name)

        # create the plugin data dir
        if not os.path.isdir(datadir + os.sep + 'plugs'):
            os.mkdir(datadir + os.sep + 'plugs')
        if not os.path.isdir(datadir + os.sep + 'plugs' + os.sep + name):
            os.mkdir(datadir + os.sep + 'plugs' + os.sep + name)

        # import the plugin
        plug = self.plugimport(mod, name)
        rlog(0, 'plugins', "%s.%s registered" % (mod, name))
        return plug

    def showregistered(self):

        """ show registered plugins. """

        self.avail.sort()
        rlog(10, 'plugins', 'registered %s' % ' .. '.join(self.avail))
        self.overload()

    def regdir(self, dirname, exclude=[]):

        """ register a directory. """

        threads = []
        plugs = []
        for plug in plugnames(dirname):
            if plug in exclude or plug.startswith('.'):
                continue
            try:
                self.regplugin(dirname, plug)
                plugs.append(plug)
            except:
                handle_exception()
        self.ondisk.extend(plugs)
        return plugs

    def regcore(self): 

        """ register core plugins. """

        self.plugdeny.init([])
        self.plugallow.init([])
        avail = [] 
        plugs = gozer_import('gozerbot.plugs')
        for i in plugs.__plugs__:
            if i not in avail:
                try:
                    self.regplugin('gozerbot.plugs', i)
                except Exception, ex:
                    handle_exception()
                avail.append(i)
        self.ondisk.extend(avail)

    def regplugins(self):

        """ register plugins. """

        self.regcore()
        avail = []

        # check for myplugs directory
        if os.path.isdir('myplugs'):
            avail.extend(self.regdir('myplugs'))  
            for i in os.listdir('myplugs'):
                if i.startswith('.'):
                    continue
                if os.path.isdir('myplugs' + os.sep + i):
                    avail.extend(self.regdir('myplugs' + os.sep + i))  
        else:
            rlog(10, 'plugins', 'no myplugs directory found')

        # check for gozerplugs package
        try:
            plugs = gozer_import('gozerplugs')
        except ImportError:
            rlog(20, 'plugins', "no gozerplugs package found")
            plugs = None
        if plugs:
            for i in plugs.__plugs__:
                if i not in avail:
                    try:
                        self.regplugin('gozerplugs', i)
                        avail.append(i)
                    except Exception, ex:
                        handle_exception()
                else:
                    rlog(10, 'plugins', '%s already loaded' % i)

        self.ondisk.extend(avail)
        self.readoverload()
        start_new_thread(self.showregistered, ())

    def readoverload(self):

        """ see if there is a permoverload file and if so use it to overload
            permissions based on function name.
        """
        try:
            overloadfile = open(datadir + os.sep + 'permoverload', 'r')
        except IOError:
            return
        try:
            for i in overloadfile:
                i = i.strip()
                splitted = i.split(',')
                try:
                    funcname = splitted[0].strip()
                    perms = []
                    for j in splitted[1:]:
                        perms.append(j.strip())
                except IndexError:
                    rlog(10, 'plugins', "permoverload: can't set perms of %s" \
% i)
                    continue
                if not funcname:
                    rlog(10, 'plugins', "permoverload: no function provided")
                    continue
                if not perms:
                    rlog(10, 'plugins', "permoverload: no permissions \
provided for %s" % funcname)
                    continue
                self.overloads[funcname] = perms
        except Exception, ex:
             handle_exception()

    def overload(self):

        """ overload functions in self.overloads. """
        for funcname, perms in self.overloads.iteritems():
           if self.permoverload(funcname, perms):
               rlog(10, 'plugins', '%s permission set to %s' % (funcname, \
perms))

    def available(self):

        """ available plugins not yet registered. """

        self.ondisk.sort()
        return self.ondisk

    def saveplug(self, plugname):

        """ call save on items in plugins savelist. """

        try:
            self.plugs[plugname].save()
        except AttributeError:
            pass
        except KeyError:
            pass

    def save(self):

        """ call registered plugins save. """

        for plug in self.plugs.values():
            try:
                plug.save()
            except AttributeError:
                pass
            except Exception, ex:
                handle_exception()

    def save_cfg(self):

        """ call registered plugins configuration save. """

        for plug in self.plugs.values():
            try:
                cfg = getattr(plug, 'cfg')
                if isinstance(cfg, PersistConfig):
                    try:
                        cfg.save()
                    except:
                        handle_exception()
            except AttributeError:
                continue

    def save_cfgname(self, name):

        """ save persisted plugin config data. """

        try:
            plug = self.plugs[name]
            cfg = getattr(plug, 'cfg')
            if isinstance(cfg, PersistConfig):
                try:
                    cfg.save()
                except:
                    handle_exception()
        except (AttributeError, KeyError):
            pass
	
    def exit(self):

        """ call registered plugins save. """

        self.save()
        threadlist = []

        # call shutdown on all plugins
        for name, plug in self.plugs.iteritems():
            try:
                shutdown = getattr(plug, 'shutdown')
                thread = start_new_thread(shutdown, ())
                threadlist.append((name, thread))
                try:
                    self.initcalled.remove(name)
                except ValueError:
                    pass
            except AttributeError:
                continue
            except Exception, ex:
                rlog(10, 'plugins', 'error shutting down %s: %s' % (name, str(ex)))

        # join shutdown threads
        try:
            for name, thread in threadlist:
                thread.join()
                rlog(10, 'plugins', '%s shutdown finished' % name)
        except:
            handle_exception()
            return

    def getoptions(self, command):
        """ return options entry of a command. """
        return cmnds.getoptions(command)

    def getdepend(self, plugname):

        """ get plugins the plugin depends on. """

        # try to import the plugin
        if plugname in self.plugs:
            plug = self.plugs[plugname]
        else:
            for mod in ['gozerbot.plugs', 'gozerplugs', 'myplugs']:
                try:
                    plug = gozer_import('%s.%s' % (mod, plugname))
                except ImportError:
                    continue

        # check for the __depend__ attribute           
        try: 
            depends = plug.__depend__
        except:
            depends = []

        return depends

    def reload(self, mod, name, enable=True):

        """ reload plugin. """

        # create the plugin data dir
        if not os.path.isdir(datadir + os.sep + 'plugs'):
            os.mkdir(datadir + os.sep + 'plugs')
        if not os.path.isdir(datadir + os.sep + 'plugs' + os.sep + name):
            os.mkdir(datadir + os.sep + 'plugs' + os.sep + name)

        reloaded = []
        modname = mod + '.' + name
        self.unload(name)
        if enable:
            self.enable(name)

        # force an import of the plugin
        plug = self.plugs[name] = force_import(modname)

        # recurse the reload function if plugin is a dir
        try:
            for p in plug.__plugs__:
                reloaded.extend(self.reload(modname, p))
        except (KeyError, AttributeError):
            pass

        # call plugins init() function
        try:
            rlog(0, 'plugins', 'calling %s init()' % modname)
            plug.init()
            self.initcalled.append(modname)
        except (AttributeError, KeyError):
            pass
        except Exception, ex:
            rlog(10, 'plugins', '%s module init failed' % name)
            raise

        rlog(0, 'plugins', 'reloaded plugin %s' % modname)
        reloaded.append(name)
        self.plugallow.data.append(name)
        self.avail.append(name)

        # recurse on plugins the depend on this plugin
        try:
            depends = plug.__depending__
            for plug in depends:
                reloaded.extend(self.reload(mod, plug, False))
        except AttributeError:
            pass

        if enable:
            self.overload()

        return reloaded

    def unload(self, plugname):

        """ unload plugin. """

        # call plugins shutdown function if available
        unloaded = [plugname, ]

        # recurse if plugin is dir
        try:
            plug = self.plugs[plugname]
            for p in plug.__plugs__:
                unloaded.extend(self.unload(p))
        except (KeyError, AttributeError):
            pass

        # save and unload
        for plugname in unloaded:
            self.saveplug(plugname)
            self.unloadnosave(plugname)

        return unloaded

    def unloadnosave(self, plugname):

        """ unload plugin without saving. """

        # call shutdown function
        try:
            self.plugs[plugname].shutdown()
            rlog(10, 'plugins', '%s shutdown called' % plugname)
        except (AttributeError, KeyError):
            pass
        except Exception, ex:
            handle_exception()

        # remove from plugallow
        try:
            self.plugallow.data.remove(plugname)
        except (KeyError, ValueError):
            pass

        # remove from avail list
        try:
            self.avail.remove(plugname)
        except ValueError:
            pass

        # remove from initcalled list
        try:
            self.initcalled.remove(plugname)
        except ValueError:
            pass

        # unload commands, RE callbacks, callbacks, monitorsetc.
        try:
            cmnds.unload(plugname)
            callbacks.unload(plugname)
            jcallbacks.unload(plugname)
            rebefore.unload(plugname)
            reafter.unload(plugname)
            saymonitor.unload(plugname)
            outmonitor.unload(plugname)
            jabbermonitor.unload(plugname)
            tests.unload(plugname)
            outputmorphs.unload(plugname)
            inputmorphs.unload(plugname)
            if self.plugs.has_key(plugname):
                del self.plugs[plugname]
        except Exception, ex:
            handle_exception()
            return 0

        rlog(0, 'plugins', '%s unloaded' % plugname)
        return 1

    def whereis(self, what):

        """ locate what in plugins. """

        return cmnds.whereis(what)

    def permoverload(self, funcname, perms):

        """ overload permission of a function. """

        if not rebefore.permoverload(funcname, perms):
            if not cmnds.permoverload(funcname, perms):
                if not reafter.permoverload(funcname, perms):
                    return 0
        return 1

    def woulddispatch(self, bot, ievent):

        """ function to determine whether a event would dispatch. """

        (what, command) = self.dispatchtest(bot, ievent)
        if what and command:
            return 1

    def dispatchtest(self, bot, ievent, direct=False):

        """ see if ievent would dispatch. """

        # check for ignore
        if shouldignore(ievent.userhost):
            return (None, None)

        # check for throttle
        if ievent.userhost in bot.throttle:
            return (None, None)

        # set target properly
        if ievent.txt.find(' | ') != -1:
            target = ievent.txt.split(' | ')[0]
        elif ievent.txt.find(' && ') != -1:
            target = ievent.txt.split(' && ')[0]
        else:
            target = ievent.txt
        result = []

        # first check for RE before commands dispatcher
        com = rebefore.getcallback(target)

        if com and not target.startswith('!'):
            com.re = True
            result = [rebefore, com]
        else:

            # try commands 
            if ievent.txt.startswith('!'):
                ievent.txt = ievent.txt[1:]

            aliascheck(ievent)
            com = cmnds.getcommand(ievent.txt)

            if com:
                com.re = False
                result = [cmnds, com]
                ievent.txt = ievent.txt.strip()
            else:

                # try RE after commands
                com = reafter.getcallback(target)
                if com:
                    com.re = True
                    result = [reafter, com]
        if result:

            # check for auto registration
            if config['auto_register'] and not users.getname(ievent.userhost):
                users.add("%s!%s" % (ievent.nick, ievent.userhost) , \
[ievent.userhost, ], ['USER', ])

            # check for anon access
            if config['anon_enable'] and not 'OPER' in result[1].perms:
                return result

            # check if command is allowed (all-add command)
            if com.name in bot.state['allowed'] or getname(com.func) in bot.state['allowed']:
                return result

            # check for channel permissions
            try:
                chanperms = bot.channels[ievent.channel.lower()]['perms']
                for i in result[1].perms:
                    if i in chanperms and not ievent.msg:
                        ievent.speed = 1
                        return result
            except (KeyError, TypeError):
                pass

            # if direct is set dont check the user database
            if direct:
                return result

            # use event.stripped in case of jabber 
            if bot.jabber and ievent.jabber:
                if not ievent.groupchat or ievent.jidchange:
                    if users.allowed(ievent.stripped, result[1].perms):
                        return result

            # irc users check
            if users.allowed(ievent.userhost, result[1].perms):
                return result

        return (None, None)

    def cmnd(self, bot, ievent, timeout=15):

        """ launch command and wait for result. """
        ii = Ircevent(ievent)
        q = Queue.Queue()
        ii.queues.append(q)
        self.trydispatch(bot, ii)
        return waitforqueue(q, timeout)

    def trydispatch(self, bot, ievent, direct=False):

        """ try to dispatch ievent. """

        # test for ignore
        if shouldignore(ievent.userhost):
            return 0

        # set printto
        if ievent.msg:
            ievent.printto = ievent.nick
        else:
            ievent.printto = ievent.channel

        # see if ievent would dispatch
        # what is rebefore, cmnds of reafter, com is the command object
        # check if redispatcher or commands object needs to be used
        (what, com) = self.dispatchtest(bot, ievent, direct)
        if what:
            if com.allowqueue:
                ievent.txt = ievent.txt.replace(' || ', ' | ')
                if ievent.txt.find(' | ') != -1:
                    if ievent.txt[0] == '!':
                        ievent.txt = ievent.txt[1:]
                    else:
                        self.splitpipe(bot, ievent)
                        return
                elif ievent.txt.find(' && ') != -1:
                    self.multiple(bot, ievent)
                    return
            return self.dispatch(what, com, bot, ievent)

    def dispatch(self, what, com, bot, ievent):

        """ do the actual dispatch  of event. """
        if bot.stopped:
            return 0

        # make command options
        if com.options:
            makeoptions(ievent, com.options)
        else:
            makeoptions(ievent)

        # make arguments and rest
        makeargrest(ievent)
        ievent.usercmnd = 1
        rlog(10, 'plugins', 'dispatching %s for %s' % (ievent.command, ievent.userhost))

        # call dispatch
        what.dispatch(com, bot, ievent)
        return 1

    def multiple(self, bot, ievent):

        """ execute multiple commands. """

        for i in ievent.txt.split(' && '):
            if not bot.jabber:
                ie = Ircevent()
                ie.copyin(ievent)
            else:
                from jabber.jabbermsg import Jabbermsg
                ie = Jabbermsg(ievent)
                ie.copyin(ievent)
            ie.txt = i.strip()
            self.trydispatch(bot, ie)

    def splitpipe(self, bot, ievent):

        """ execute commands in a pipeline. """

        origqueues = ievent.queues
        ievent.queues = []
        events = []
        txt = ievent.txt.replace(' || ', ' ##')

        # split commands
        for i in txt.split(' | '):
            item = i.replace(' ##', ' | ')
            if not ievent.jabber:
                ie = Ircevent()
                ie.copyin(ievent)
            else:
                from jabber.jabbermsg import Jabbermsg
                ie = Jabbermsg(ievent.orig)
                ie.copyin(ievent)
            ie.txt = item.strip()
            events.append(ie)

        # loop over events .. chain queues
        prevq = None
        for i in events[:-1]:
            q = Queue.Queue()
            i.queues.append(q)
            if prevq:
                i.inqueue = prevq
            prevq = q
        events[-1].inqueue = prevq
        if origqueues:
            events[-1].queues = origqueues

        # check if all commands would dispatch
        for i in events:
            if not self.woulddispatch(bot, i):
                ievent.reply("can't execute %s" % str(i.txt))
                return

        # do the dispatch
        for i in events:
            (what, com) = self.dispatchtest(bot, i)
            if what:
                self.dispatch(what, com, bot, i)

    def listreload(self, pluglist):

        """ reload list of plugins. """

        failed = []

        # loop over the plugin list and reload them
        for what in pluglist:
            splitted = what[:-3].split(os.sep)
            mod = '.'.join(splitted[:-1])
            if not mod:
                mod = 'gozerplugs'
            plug  = splitted[-1]

            # reload the plugin
            try:
                self.reload(mod, plug)
            except Exception, ex:
                failed.append(what)
        return failed

# THE plugins object
plugins = Plugins()
