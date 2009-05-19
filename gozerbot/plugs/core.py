# plugs/core.py
#
#

""" core bot commands. """


__copyright__ = 'this file is in the public domain'
__gendocskip__ = ['userhostcache', ]

# gozerbot imports
from gozerbot.generic import getwho, die, reboot, elapsedstring, reboot_stateful, getversion, cleanpyc, handle_exception
from gozerbot.exit import globalshutdown
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.callbacks import callbacks
from gozerbot.redispatcher import rebefore, reafter
from gozerbot.plugins import plugins
from gozerbot.users import users
from gozerbot.partyline import partyline
from gozerbot.fleet import fleet
from gozerbot.config import config
from gozerbot.utils.statdict import Statdict
from gozerbot.aliases import aliases, aliasreverse, aliasset
from gozerbot.partyline import partyline
from gozerbot.plughelp import plughelp
from gozerbot.eventhandler import mainhandler
from gozerbot.runner import cbrunners, cmndrunners
from gozerbot.tests import tests
import gozerbot.utils.log

# basic imports
from sets import Set
import time, threading, sys, re, os, resource

plughelp.add('core', 'core commands for the bot')

def handle_rusage(bot, ievent):

    """ show resource usage. """

    ievent.reply('resources: %s' % str(resource.getrusage(resource.RUSAGE_SELF)))

cmnds.add('rusage', handle_rusage, 'OPER')
examples.add('rusage', 'show rusage of the bot', 'rusage')
tests.add('rusage', 'ru_stime')

def handle_options(bot, ievent):

    """ show possible options of a command. """

    if not ievent.rest:
        ievent.missing('<command>')
        return

    options = plugins.getoptions(ievent.rest)

    if options:
        ievent.reply("the following options are available for command %s: " % \
ievent.rest, options.keys())
    else:
        ievent.reply('no command options found for %s' % ievent.rest)

cmnds.add('options', handle_options, ['USER', 'OPER'])
examples.add('options', 'show what options are available for a command', 'options')
tests.add('options', '--chan')

def handle_whatperms(bot, ievent):

    """ show possible permissions. """

    ievent.reply("the following permission are available: ", plugins.whatperms())

cmnds.add('whatperms', handle_whatperms, ['USER', 'OPER'])
examples.add('whatperms', 'show what permissions are available', 'whatperms')
tests.add('whatperms', 'USER')

def handle_encoding(bot, ievent):

    """ show default encoding. """

    ievent.reply('default encoding is %s' % sys.getdefaultencoding())

cmnds.add('encoding', handle_encoding, ['USER', 'OPER'])
examples.add('encoding', 'show default encoding', 'encoding')
tests.add('encoding')

def handle_uptime(bot, ievent):

    """ show uptime. """

    ievent.reply("uptime is %s" % elapsedstring(time.time()-bot.starttime))

cmnds.add('uptime', handle_uptime, ['USER', 'WEB', 'JCOLL'])
examples.add('uptime', 'show uptime of the bot', 'uptime')
aliasset('up', 'uptime')
tests.add('uptime', 'uptime is')

def handle_userhostcache(bot, ievent):

    """ show bots userhost cache. """

    ievent.reply(str(bot.userhosts.data))

cmnds.add('userhostcache', handle_userhostcache, 'OPER')
tests.add('userhostcache', 'dunker')

def handle_list(bot, ievent):

    """ list [<plugin>] .. list loaded plugins or list commands provided by \
        plugin.
    """

    try:
        what = ievent.args[0]
    except:
        # no arguments given .. show plugins
        ievent.reply('\002loaded plugins:\002 ', plugins.list())
        return

    # show commands of <what> plugin
    result = []

    for i, j in cmnds.items():
        if what == j.plugname:
            txt = ""
            alias = aliasreverse(i)
            if alias:
                txt += "%s (%s)" % (i, alias)
            else:
                txt = i
            if txt:
                result.append(txt)

    if result:
        result.sort()
        ievent.reply('%s has the following commands: ' % what, result)
    else:
        ievent.reply('no commands found for plugin %s' % what)

cmnds.add('list', handle_list, ['USER', 'WEB', 'CLOUD'], threaded=True)
examples.add('list', 'list registered plugins or list commands in plugin', '1) list 2) list rss')
tests.add('list', 'core')

def handle_available(bot, ievent):

    """ available .. show what plugins are available. """

    l = Set(plugins.list())
    ondisk = Set(plugins.available())
    diff = list(ondisk - l)    
    diff.sort()
    ievent.reply('\002available plugins:\002 (reload to enable): ', diff)

cmnds.add('available', handle_available, ['USER', 'WEB'])
examples.add('available', 'show what plugins are available but not loaded (see the list command for loaded plugins)', 'available')
aliasset('avail', ' available')
aliasset('plugins', 'available')
tests.add('avail')

def doquit(bot, ievent):

    """ quit the bot. """

    globalshutdown()

cmnds.add('quit', doquit, 'OPER')
examples.add('quit', 'quit the bot', 'quit')
aliasset('shutdown', 'quit')
aliasset('exit', 'quit')
aliasset('halt', 'quit')

def handle_reboot(bot, ievent):

    """ reboot .. reboot the bot. """

    ievent.reply('rebooting')
    global backupstop
    stateful = True

    if ievent.rest == 'cold':
        stateful = False

    time.sleep(2)

    try: 
        backupstop = 1
        if not stateful:
            fleet.exit()
        else:
            fleet.exit(jabber=True)
        plugins.exit()
    finally:
        if stateful:
            mainhandler.put(0, reboot_stateful, bot, ievent, fleet, partyline)
        else:
            mainhandler.put(0, reboot)

cmnds.add('reboot', handle_reboot, 'OPER')
examples.add('reboot', 'restart the bot', 'reboot')

def handle_commands(bot, ievent):

    """ commands <plugin> .. show commands of <plugin>. """

    try:
        plugin = ievent.args[0].lower()
    except IndexError:
        ievent.missing('<plugin> .. see the list command for available \
plugins')
        return

    if not plugins.plugs.has_key(plugin):
        ievent.reply('no %s plugin is loaded .. see the available command for \
available plugins (reload to enable)' % plugin)
        return

    result = []

    for i, j in cmnds.iteritems():
        if plugin == j.plugname:
            txt = ""
            alias = aliasreverse(i)
            if alias:
                txt += "%s (%s)" % (i, alias)
            else:
                txt = i
            if txt:
                result.append(txt)

    if result:
        result.sort()
        ievent.reply('%s has the following commands: ' % plugin, result, \
dot=True)
    else:
        ievent.reply('no commands found for plugin %s' % plugin)

cmnds.add('commands', handle_commands, ['USER', 'WEB', 'CLOUD'])
examples.add('commands', 'show commands of <plugin>', '1) commands core')
tests.add('commands core', 'uptime')

def handle_perm(bot, ievent):

    """ perm <command> .. get permission of command. """

    try:
        cmnd = ievent.args[0]
    except IndexError:
        ievent.missing("<cmnd>")
        return

    try:
        cmnd = aliases.data[cmnd]
    except KeyError:
        pass

    perms = cmnds.perms(cmnd)

    if perms:
        ievent.reply("%s command needs %s permission" % (cmnd, perms))
        return

    ievent.reply("can't find perm for %s" % cmnd)

cmnds.add('perm', handle_perm, ['USER', 'WEB'])
examples.add('perm', 'show permission of command', 'perm quit')
tests.add('perm version', 'USER')

def handle_cc(bot, ievent):

    """ cc [<controlchar>] .. set/get control character of channel. """

    try:
        chan = ievent.args[1].lower()
    except IndexError:
        chan = ievent.channel.lower()

    try:
        what = ievent.args[0]

        if not users.allowed(ievent.userhost, 'OPER'):
            return

        if len(what) > 1:
            ievent.reply("only one character is allowed")
            return

        try:
            bot.channels[chan]['cc'] = what
        except (KeyError, TypeError):
            ievent.reply("no channel %s in database" % chan)
            return

        bot.channels.save()
        ievent.reply('control char set to %s' % what)
    except IndexError:
        # no argument given .. show cc of channel command is given in
        try:
            cchar = bot.channels[chan]['cc']
            ievent.reply('control character(s) for channel %s are/is %s' % \
(chan, cchar))
        except (KeyError, TypeError):
            ievent.reply("default cc is %s" % config['defaultcc'])

cmnds.add('cc', handle_cc, 'USER', allowqueue=False)
examples.add('cc', 'set control char of channel or show control char of channel','1) cc ! 2) cc')
tests.add('cc --chan #dunkbots', '!')
tests.add('cc --chan #dunkbots !', '!')

def handle_ccadd(bot, ievent):

    """ add a control char to the channels cc list. """

    try:
        chan = ievent.args[1].lower()
    except IndexError:
        chan = ievent.channel.lower()

    try:
        what = ievent.args[0]

        if not users.allowed(ievent.userhost, 'OPER'):
            return

        if len(what) > 1:
            ievent.reply("only one character is allowed")
            return

        try:
            bot.channels[chan]['cc'] += what
        except (KeyError, TypeError):
            ievent.reply("no channel %s in database" % chan)
            return

        bot.channels.save()
        ievent.reply('control char %s added' % what)
    except IndexError:
        ievent.missing('<cc> [<channel>]')

cmnds.add('cc-add', handle_ccadd, 'OPER', allowqueue=False)
examples.add('cc-add', 'cc-add <control char> .. add control character', 'cc-add #')
tests.add('cc-add --chan #dunkbots @', '@').add('cc-del --chan #dunkbots @')

def handle_ccdel(bot, ievent):

    """ remove a control char from the channels cc list. """

    try:
        chan = ievent.args[1].lower()
    except IndexError:
        chan = ievent.channel.lower()

    try:
        what = ievent.args[0]

        if not users.allowed(ievent.userhost, 'OPER'):
            return

        if len(what) > 1:
            ievent.reply("only one character is allowed")
            return

        try:
            bot.channels[chan]['cc'] = \
bot.channels[chan]['cc'].replace(what, '')
        except KeyError:
            ievent.reply("no channel %s in database")
            return
        except TypeError:
            ievent.reply("no channel %s in database" % chan)
            return

        bot.channels.save()
        ievent.reply('control char %s deleted' % what)

    except IndexError:
        ievent.missing('<cc> [<channel>]')

cmnds.add('cc-del', handle_ccdel, 'OPER')
examples.add('cc-del', 'cc-del <control character> .. remove cc', 'cc-del #')
tests.add('cc-add --chan #dunkbots @').add('cc-del --chan #dunkbots @', '@')

def handle_intro(bot, ievent):

    """ intro <nick> .. do whois on nick to sync userhosts cache. """

    if not bot.type == 'irc':
        ievent.reply("intro only works on irc bots")
        return

    try:
        who = ievent.args[0]
    except IndexError:
        ievent.reply("intro <nick>")
        return

    bot.whois(who)
    ievent.reply('whois command send')

cmnds.add('intro', handle_intro, 'OPER')
examples.add('intro', 'do a whois of <nick> to sync userhost into the userhost cache', 'intro dunker')
tests.add('intro dunker')

def handle_loglevel(bot, ievent):

    """ loglevel <level> .. get or set loglevel. the lower the more the bot logs. """

    if len(ievent.args) == 0:
        ievent.reply('loglevel is %s' % config['loglevel'])
        return

    try:
        level = int(ievent.args[0])
    except ValueError:
        ievent.reply('i need a integer argument')
        return

    config.set('loglevel', level)
    gozerbot.utils.log.loglevel = level
    ievent.reply('loglevel is now %s' % config['loglevel'])

cmnds.add('loglevel', handle_loglevel,'OPER')
examples.add('loglevel', 'get/set current loglevel .. the lower the loglevel the more the bot logs', '1) loglevel 2) loglevel 10')
tests.add('loglevel 10', 'is now 10').add('loglevel', '10')

def handle_loglist(bot, ievent):

    """ loglist <plugin> .. get or set loglist .. loglist is a list of plugins 
        to log.
    """

    if config['loglist'] == None:
        config['loglist'] = []

    for plugin in ievent.args:
        if plugin not in config['loglist']:
            config['loglist'].append(plugin)
        if plugin not in gozerbot.utils.log.loglist:
            gozerbot.utils.log.loglist.append(plugin)
        config.save()

    ievent.reply('loglist is now %s' % config['loglist'])

cmnds.add('loglist', handle_loglist,'OPER')
examples.add('loglist', 'get loglist or add plugin to loglist', '1) loglist 2) loglist rss')
tests.add('loglist rss', 'rss').add('loglist', 'rss')

def handle_loglistdel(bot, ievent):

    """ loglist-del <plugin> .. delete plugin from loglist. """

    if config['loglist'] == None:
        config['loglist'] = []

    for plugin in ievent.args:

        try:
            config['loglist'].remove(plugin)
        except ValueError:
            pass

        try:
            gozerbot.utils.log.loglist.remove(plugin)
        except ValueError:
            pass

        config.save()

    ievent.reply('loglist is now %s' % config['loglist'])
 
cmnds.add('loglist-del', handle_loglistdel,'OPER')
examples.add('loglist-del', 'remove plugin from loglist', 'loglist-del rss')
tests.add('loglist rss', 'rss').add('loglist-del')

def handle_partylist(bot, ievent):

    """ partylist .. show users on partylist. """

    partynicks = partyline.list_nicks()

    if partynicks:
        ievent.reply("people on partyline: ", partynicks)
    else:
        ievent.reply('no party yet!')

cmnds.add('partylist', handle_partylist, ['USER', 'WEB'])
examples.add('partylist', 'show connected partylist users', 'partylist')
tests.add('partylist')

def handle_partysilent(bot, ievent):

    """ party-silent .. disable partyline noise. """

    partyline.silent(ievent.nick)
    ievent.reply('partyline put to silent mode')

cmnds.add('party-silent', handle_partysilent, ['USER', ])
examples.add('party-silent', 'disable partyline noise', 'party-silent')
tests.add('party-silent')

def handle_partyloud(bot, ievent):

    """ party-loud .. enable partyline noise. """

    partyline.loud(ievent.nick)
    ievent.reply('partyline put to loud mode')

cmnds.add('party-loud', handle_partyloud, ['USER', ])
examples.add('party-loud', 'enable partyline noise', 'party-loud')
tests.add('party-loud')

def handle_threads(bot, ievent):

    """ show running threads. """

    stats = Statdict()
    threadlist = threading.enumerate()

    for thread in threadlist:
        stats.upitem(thread.getName())

    result = []

    for item in stats.top():
        result.append("%s = %s" % (item[0], item[1]))

    result.sort()
    ievent.reply("threads running: ", result)

cmnds.add('threads', handle_threads, ['USER', 'OPER'])
examples.add('threads', 'show running threads', 'thread')
tests.add('threads', 'Bot')

def handle_running(bot, ievent):

    """ running .. show running jobs on the runner. """

    stats = [Statdict() for i in range(10)]
    teller = 0

    for runners in cbrunners:
        for runner in runners.running():
            stats[teller].upitem(runner)
        teller += 1

    teller = 0

    for runners in cmndrunners:
        for runner in runners.running():
            stats[teller].upitem(runner)
        teller += 1

    result = []

    for i in range(teller):
        for item in stats[i].top():
            result.append("%s.%s = %s" % (item[0], 10-i, item[1]))

    result.sort()
    ievent.reply("runners: ", result)

cmnds.add('running', handle_running, ['USER', 'OPER'])
examples.add('running', 'show running jobs', 'running')
tests.add('running')

def handle_nowrunning(bot, ievent):
    result = []

    for runners in cbrunners:
        for runner in runners.runners:
            result.append(runner.nowrunning)

    ievent.reply('nowrunning callbacks: %s' % str(result))
    result = []

    for runners in cmndrunners:
        for runner in runners.runners:
            result.append(runner.nowrunning)

    ievent.reply('nowrunning commands: %s' % str(result))

cmnds.add('nowrunning', handle_nowrunning, 'OPER')
tests.add('nowrunning')

def handle_callbacks(bot, ievent):

    """ list all callbacks. """

    ievent.reply(callbacks.list())

cmnds.add('callbacks', handle_callbacks, 'OPER')
tests.add('callbacks')

def handle_save(bot, ievent):

    """ save bot data to disk """

    ievent.reply('saving')
    plugins.save()
    fleet.save()
    config.save()
    ievent.reply('done')

cmnds.add('save', handle_save, 'OPER')
examples.add('save', 'save bot data', 'save')
tests.add('save', 'done')

def handle_version(bot, ievent):

    """ show bot's version. """

    ievent.reply(getversion())

cmnds.add('version', handle_version, ['USER', 'WEB', 'JCOLL', 'CLOUD'])
examples.add('version', 'show version of the bot', 'version')
aliasset('v', 'version')
tests.add('version', 'GOZERBOT')

def handle_whereis(bot, ievent):

    """ whereis <cmnd> .. locate a command. """

    try:
        cmnd = ievent.args[0]
    except IndexError:
        ievent.missing('<cmnd>')
        return

    plugs = plugins.whereis(cmnd)

    if plugs:
        ievent.reply("%s command is in: " %  cmnd, plugs)
    else:
        ievent.reply("can't find " + cmnd)

cmnds.add('whereis', handle_whereis, ['USER', 'WEB'])
examples.add('whereis', 'whereis <cmnd> .. show in which plugins <what> is', 'whereis test')
tests.add('whereis version', 'core')

def handle_help(bot, ievent):

    """ help [<cmnd>|<plugin>] .. show help on plugin/command or show basic help msg. """

    try:
        what = ievent.args[0]
    except IndexError:
        ievent.reply('help <cmnd> or help <plugin> .. see the !list \
command for a list of available plugins or see !available command for a list \
of plugins to be reloaded')
        return

    phelp = plughelp.get(what)
    cmndresult = []

    if phelp:
        ievent.reply('plugin description: %s' % phelp)
        perms = list(users.getperms(ievent.userhost))

        for i, j in cmnds.iteritems():
            if what == j.plugname:
                for perm in j.perms:
                    if perm in perms:
                        if i not in cmndresult:
                            cmndresult.append(i)

        if cmndresult:
            cmndresult.sort()
            resultstr = ""
            for i in cmndresult:
                alias = aliasreverse(i)
                if alias:
                    resultstr += "%s (%s) .. " % (i, alias)
                else:
                    resultstr += "%s .. " % i
            ievent.reply('commands: %s'\
 % resultstr[:-4])
        else:
            ievent.reply('no commands available for permission %s' % \
str(perms))

        result = []

        for i in rebefore.relist:
            if what == i.plugname:
                if users.allowed(ievent.userhost, i.perms):
                    result.append(i.regex)

        for i in reafter.relist:
            if what == i.plugname:
                if users.allowed(ievent.userhost, i.perms):
                    result.append(i.regex)

        if result:
            resultstr = ""
            for i in result:
                resultstr += '"%s" .. ' % i
            ievent.reply('regular expressions: %s' % resultstr[:-4])
        else:
            pass

        result = []

        for i, j in callbacks.cbs.items():
            for z in j:
                if what == z.plugname:
                    result.append(i)

        if result:
            resultstr = ""
            for i in result:
                resultstr += "%s .. " % i
            ievent.reply('callbacks: %s' % resultstr[:-4])
        else:
            pass

        if not cmndresult:
            return

    if what in aliases.data:
        ievent.reply('%s is an alias for %s' % (what, aliases.data[what]))
        what = aliases.data[what]

    try:
        example = examples[what]
    except KeyError:
        return

    ievent.reply('%s .. alias: %s .. examples: %s' % (example.descr, aliasreverse(what), example.example))

cmnds.add('help', handle_help, ['USER', 'WEB'])
examples.add('help', 'get help on <cmnd> or <plugin>', '1) help test 2) help misc')
tests.add('help core', 'version')

def handle_apro(bot, ievent):

    """ apro <cmnd> .. apropos for command. """

    try:
        what = ievent.args[0]
    except IndexError:
        ievent.missing('<what>')
        return

    result = []
    perms = users.getperms(ievent.userhost)

    for i in cmnds.apropos(re.escape(what), perms=perms):
        alias = aliasreverse(i)
        if alias:
            result.append('%s (%s)' % (i, alias))
        else:
            result.append(i)

    res = []

    for alias in aliases.data:
        if what in alias and not what in result:
            res.append(alias)

    result.extend(res)

    if result:
        ievent.reply("commands matching %s: " % what, result , nr=1)
    else: 
        ievent.reply('no matching commands found for %s' % what)

cmnds.add('apro', handle_apro, ['USER', 'WEB'])
aliases.data['apropos'] = 'apro'
examples.add('apro', 'apro <what> .. search for commands that contain <what>', 'apro com')
tests.add('apro ver', 'version')

def handle_u(bot, ievent):

    """ u <nick> .. show userhost entry in cache. """

    try:
        nick = ievent.args[0]
    except IndexError:
        ievent.missing('<nick>')
        return

    result = getwho(bot, nick)

    if result:
        ievent.reply(result)
    else:
        ievent.reply("can't get userhost for %s" % nick)

cmnds.add('u', handle_u, ['USER', ])
examples.add('u', 'u <nick> .. get userhost cache entry for <nick>', 'u dunker')
tests.add('u dunker')

def handle_less(bot, ievent):

    """ get entry from the output cache. """

    try:
        if len(ievent.args) == 3:
            (who, index1, index2) = ievent.args
        elif len(ievent.args) == 2:
            if bot.jabber: 
                who = ievent.userhost
            else:
                who = ievent.nick
            (index1, index2) = ievent.args
        else:
            if bot.jabber:
                who = ievent.userhost
            else:
                who = ievent.nick
            index1 = 0
            index2 = ievent.args[0]
        index1 = int(index1)
        index2 = int(index2)
    except IndexError:
        ievent.missing('[<who>] [<index1>] <index2>')
        return
    except ValueError:
        ievent.reply('i need integers as arguments')
        return

    txt = bot.less.get(who, index1, index2)

    if not txt:
        ievent.reply('no data available for %s %s %s' % \
(who, index1, index2))
        return

    if bot.jabber:
        bot.say(ievent.userhost, txt)
    else:
        ievent.reply(txt)

cmnds.add('less', handle_less, ['USER', 'CLOUD'])
examples.add('less', "less [<who>] [<index1>] <index2> .. get txt from bots output cache", '1) less 0 2) less 0 2 3) less bart 1 0')
tests.add('less 0 0')

def handle_lesssize(bot, ievent):

    """ show size of output cache. """

    try:
        who = ievent.args[0]
    except IndexError:
        who = ievent.nick

    ievent.reply(bot.less.size(who))

cmnds.add('less-size', handle_lesssize, ['USER', ])
examples.add('less-size', "show sizes of data in bot's ouput cache", 'less-size')
tests.add('less-size')

def handle_more(bot, ievent):

    """ pop message from the output cache. """

    try:
        who = ievent.args[0]
    except IndexError:
        if bot.jabber:
            who = ievent.userhost
        else:
            who = ievent.nick

    what, size = bot.less.more(who, 0)

    if not what:
        ievent.reply('no more data available for %s' % who)
        return

    if bot.jabber:
        if size:
            bot.say(ievent.userhost, "%s (+%s)" % (what, size))
        else:
            ievent.reply(what)
        return      

    if size:

        # check if bot is in notice mode
        notice = False

        try:
            notice = bot.channels[ievent.printto]['notice']
        except (KeyError, TypeError):
            pass

        # check if bot is in silent mode
        silent = False

        try:
            silent = bot.channels[ievent.printto]['silent']
        except (KeyError, TypeError):
            pass

        if notice:
            how = 'notice'
        else:
            how = 'msg'

        if silent:
            printto = ievent.nick
        else:
            printto = ievent.printto

        bot.output(printto,"%s \002(+%s)\002" % (what, size), how)
    else:
        ievent.reply(what)
     
cmnds.add('more', handle_more, ['USER', 'CLOUD'], threaded=True)
examples.add('more', 'return txt from output cache', '1) more 2) more test')
tests.add('more')

def handle_whatcommands(bot, ievent):

    """ show all commands with permission. """

    if not ievent.rest:
        ievent.missing('<perm>')
        return

    result = cmnds.list(ievent.rest)
    result.sort()

    if not result:
        ievent.reply('no commands known for permission %s' % ievent.rest)
    else:
        ievent.reply('commands known for permission %s: ' % ievent.rest, result)

cmnds.add('whatcommands', handle_whatcommands, 'USER')
examples.add('whatcommands', 'show commands with permission <perm>', 'whatcommands USER')
tests.add('whatcommands USER', 'version')

def handle_cleanpyc(bot, ievent):

    """ clean pyc files. """

    removed = cleanpyc()
    ievent.reply('removed: ', removed, dot=True)

cmnds.add('cleanpyc', handle_cleanpyc, 'OPER')
tests.add('cleanpyc')
