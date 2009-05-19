# plugs/irc.py
#
#

""" irc related commands. """

__copyright__ = 'this file is in the public domain'
__gendocfirst__ = ['reconnect', 'join']
__gendoclast__ = ['part', ]

# gozerbot imports
from gozerbot.callbacks import callbacks
from gozerbot.fleet import fleet
from gozerbot.partyline import partyline
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
from gozerbot.tests import tests
import gozerbot.threads.thr as thr

# basic imports
import Queue, sets

plughelp.add('irc', 'irc related commands')

ignorenicks = []

def handle_broadcast(bot, ievent):

    """ broadcast txt to all joined channels. """

    if not ievent.rest:
         ievent.missing('<txt>')
         return

    fleet.broadcast(ievent.rest)
    partyline.say_broadcast(ievent.rest)

cmnds.add('broadcast', handle_broadcast, 'OPER')
examples.add('broadcast', 'send a message to all channels and dcc users', 'broadcast good morning')
tests.add('broadcast testing testing')

def handle_alternick(bot, ievent):

    """ set alternative nick used if nick is already taken. """

    try:
        nick = ievent.args[0]
    except IndexError:
        ievent.reply('alternick is %s' % bot.state['alternick'])
        return

    bot.state['alternick'] = nick
    bot.state.save()
    ievent.reply('alternick changed to %s' % nick)

cmnds.add('alternick', handle_alternick, 'OPER')
examples.add('alternick', 'get/set alertnick' , '1) alternick 2) alternick gozerbot2')
tests.add('alternick testbot', 'testbot')

def dojoin(bot, ievent):

    """ join <channel> [password]. """

    try:
        channel = ievent.args[0]
    except IndexError:
        ievent.missing("<channel> [password]")
        return

    try:
        password = ievent.args[1]
    except IndexError:
        password = None

    bot.join(channel, password=password)

cmnds.add('join', dojoin, ['OPER', 'JOIN'])
examples.add('join', 'join <channel> [password]', '1) join #test 2) join #test mekker')
tests.add('join #dunkbots')

def delchan(bot, ievent):

    """ delchan <channel>  .. remove channel from bot.channels. """

    try:
        chan = ievent.args[0]
    except IndexError:
        ievent.missing("<channel>")
        return

    try:
        del bot.channels.data[chan.lower()]
    except KeyError:
        ievent.reply("no channel %s in database" % chan)
        return

    bot.channels.save()	
    ievent.reply('%s deleted' % chan)

cmnds.add('delchan', delchan, 'OPER')
examples.add('delchan', 'delchan <channel> .. remove channel from bot.channels', 'delchan #mekker')

def dopart(bot, ievent):

    """ part [<channel>]. """

    if not ievent.rest:
        chan = ievent.channel
    else:
        chan = ievent.rest

    bot.part(chan)

cmnds.add('part', dopart, 'OPER')
examples.add('part', 'part [<channel>]', '1) part 2) part #test')
tests.add('part #mekker')

def handle_channels(bot, ievent):

    """ channels .. show joined channels. """

    chans = bot.state['joinedchannels']

    if chans:
        ievent.reply("joined channels: ", chans, dot=True)
    else:
        ievent.reply('no channels joined')

cmnds.add('channels', handle_channels, ['USER', 'WEB'])
examples.add('channels', 'show what channels the bot is on', 'channels')
tests.add('channels', '#dunkbots')

def handle_chat(bot, ievent):

    """ chat .. start a bot initiated dcc chat session. """

    if not bot.type == 'irc':
        ievent.reply("chat only works on irc bots")
        return

    i = ievent
    thr.start_new_thread(bot._dcclisten, (i.nick, i.userhost, i.channel))
    ievent.reply('dcc chat request sent')

cmnds.add('chat', handle_chat, 'USER')
examples.add('chat', 'start a dcc chat session', 'chat')
tests.add('chat', 'sent')

def handle_cycle(bot, ievent):

    """ cycle .. recycle channel. """

    bot.part(ievent.channel)
    try:
        key = bot.channels[ievent.channel.lower()]['key']
    except (KeyError, TypeError):
        key = None

    bot.join(ievent.channel, password=key)

cmnds.add('cycle', handle_cycle, 'OPER')
examples.add('cycle', 'part/join channel', 'cycle')
tests.add('cycle')

def handle_jump(bot, ievent):

    """ jump <server> <port> .. change server. """

    if bot.jabber:
        ievent.reply('jump only works on irc bots')
        return
    if len(ievent.args) != 2:
        ievent.missing('<server> <port>')
        return
    (server, port) = ievent.args
    ievent.reply('changing to server %s' % server)
    bot.shutdown()
    bot.server = server
    bot.port = port
    bot.connect()

cmnds.add('jump', handle_jump, 'OPER')
examples.add('jump', 'jump <server> <port> .. switch server', 'jump localhost 6667')

def modecb(bot, ievent):

    """ callback to detect change of channel key. """

    if ievent.postfix.find('+k') != -1:
        key = ievent.postfix.split('+k')[1]
        bot.channels[ievent.channel.lower()]['key'] = key

callbacks.add('MODE', modecb)

def handle_nick(bot, ievent):

    """ nick <nickname> .. change bot's nick. """

    if bot.jabber:
        ievent.reply('nick works only on irc bots')
        return

    try:
        nick = ievent.args[0]
    except IndexError:
        ievent.missing('<nickname>')
        return

    bot.donick(nick, setorig=1, save=1)

cmnds.add('nick', handle_nick, 'OPER', threaded=True)
examples.add('nick', 'nick <nickname> .. set nick of the bot', 'nick mekker')
tests.add('nick miep')

def handle_sendraw(bot, ievent):

    """ sendraw <txt> .. send raw text to the server. """

    bot.sendraw(ievent.rest)

cmnds.add('sendraw', handle_sendraw, 'SENDRAW')
examples.add('sendraw', 'sendraw <txt> .. send raw string to the server', \
'sendraw PRIVMSG #test :yo!')

def handle_nicks(bot, ievent):

    """ return nicks on channel. """

    if bot.jabber:
        ievent.reply('nicks only works on irc bots')
        return

    try:
        chan = ievent.args[0]
    except IndexError:
        chan = ievent.channel

    queue = Queue.Queue()
    # set callback for name info response
    wait353 = bot.wait.register('353', chan, queue)
    # 366 is end of names response list
    wait366 = bot.wait.register('366', chan, queue)
    result = ""
    bot.names(chan)

    while(1):
        qres = queue.get()
        if qres == None:
            break
        if qres.cmnd == '366':
            break
        else:
            result += "%s " % qres.txt

    bot.wait.delete(wait353)
    bot.wait.delete(wait366)

    if result:
        res = result.split()

        for nick in res:
            for i in ignorenicks:
                if i in nick:
                    try:
                        res.remove(nick)
                    except ValueError:
                        pass

        res.sort()
        ievent.reply("nicks on %s (%s): " % (chan, bot.server), res)
    else:
        ievent.reply("can't get nicks of channel %s" % chan)

cmnds.add('nicks', handle_nicks, ['OPER', 'WEB'], threaded=True)
examples.add('nicks', 'show nicks on channel the command was given in', 'nicks')
tests.add('nicks', 'test')

def handle_silent(bot, ievent):

    """ set silent mode of channel. """

    if ievent.rest:
        channel = ievent.rest.split()[0].lower()
    else:
        if ievent.cmnd == 'DCC':
            return
        channel = ievent.channel

    ievent.reply('putting %s to silent mode' % channel)

    try:
        bot.channels[channel]['silent'] = 1
    except (KeyError, TypeError):
        ievent.reply("no %s channel in database" % channel)
        return 

cmnds.add('silent', handle_silent, 'OPER')
examples.add('silent', 'set silent mode on channel the command was given in', 'silent')
tests.add('silent').add('loud')

def handle_loud(bot, ievent):

    """ loud .. enable output to the channel. """

    if ievent.rest:
        channel = ievent.rest.split()[0].lower()
    else:
        if ievent.cmnd == 'DCC':
            return
        channel = ievent.channel

    try:
        bot.channels[channel]['silent'] = 0
    except (KeyError, TypeError):
        ievent.reply("no %s channel in database" % channel)
        return 

    ievent.reply('%s put into loud mode' % ievent.channel)

cmnds.add('loud', handle_loud, 'OPER')
examples.add('loud', 'disable silent mode of channel command was given in', 'loud')
tests.add('loud')

def handle_withnotice(bot, ievent):

    """ withnotice .. make bot use notice in channel. """

    if ievent.rest:
        channel = ievent.rest.split()[0].lower()
    else:
        if ievent.cmnd == 'DCC':
            return
        channel = ievent.channel

    try:
        bot.channels[channel]['notice'] = 1
    except (KeyError, TypeError):
        ievent.reply("no %s channel in database" % channel)
        return 

    ievent.reply('now using notice in %s' % channel)
    
cmnds.add('withnotice', handle_withnotice, 'OPER')
examples.add('withnotice', 'make bot use notice on channel the command was given in', 'withnotice')
tests.add('withnotice').add('withprivmsg')

def handle_withprivmsg(bot, ievent):

    """ withprivmsg .. make bot use privmsg in channel. """

    if ievent.rest:
        channel = ievent.rest.split()[0].lower()
    else:
        if ievent.cmnd == 'DCC':
            return
        channel = ievent.channel

    try:
        bot.channels[channel]['notice'] = 0
    except (KeyError, TypeError):
        ievent.reply("no %s channel in database" % channel)
        return 

    ievent.reply('now using privmsg in %s' % ievent.channel)

cmnds.add('withprivmsg', handle_withprivmsg, 'OPER')
examples.add('withprivmsg', 'make bot use privmsg on channel command was given in', 'withprivmsg')
tests.add('withprivmsg')

def handle_reconnect(bot, ievent):

    """ reconnect .. reconnect to server. """

    ievent.reply('reconnecting')
    bot.reconnect()

cmnds.add('reconnect', handle_reconnect, 'OPER', threaded=True)
examples.add('reconnect', 'reconnect to server', 'reconnect')

def handle_channelmode(bot, ievent):

    """ show channel mode. """

    if bot.type != 'irc':
        ievent.reply('channelmode only works on irc bots')
        return

    try:
        chan = ievent.args[0].lower()
    except IndexError:
        chan = ievent.channel.lower()

    if not chan in bot.state['joinedchannels']:
        ievent.reply("i'm not on channel %s" % chan)
        return

    ievent.reply('channel mode of %s is %s' % (chan, bot.channels.get(chan, 'mode')))

cmnds.add('channelmode', handle_channelmode, 'OPER')
examples.add('channelmode', 'show mode of channel', '1) channelmode 2) channelmode #test')
tests.add('channelmode --chan #dunkbots')

def handle_action(bot, ievent):

    """ make the bot send an action string. """

    try:
        channel, txt = ievent.rest.split(' ', 1)
    except ValueError:
        ievent.missing('<channel> <txt>')
        return

    bot.action(channel, txt)

cmnds.add('action', handle_action, ['ACTION', 'OPER'], speed=1)
examples.add('action', 'send an action message', 'action #test yoo dudes')
tests.add('action #dunkbots mekker')

def handle_say(bot, ievent):

    """ make the bot say something. """

    try:
        channel, txt = ievent.rest.split(' ', 1)
    except ValueError:
        ievent.missing('<channel> <txt>')
        return

    bot.say(channel, txt)

cmnds.add('say', handle_say, ['SAY', 'OPER'], speed=1)
examples.add('say', 'send txt to channel/user', 'say #test good morning')
tests.add('say #dunkbots mekkerbot')

def handle_server(bot, ievent):

    """ show the server to which the bot is connected. """

    ievent.reply(bot.server)

cmnds.add('server', handle_server, 'OPER')
examples.add('server', 'show server hostname of bot', 'server')
tests.add('server')

def handle_voice(bot, ievent):

    """ give voice. """

    if bot.type != 'irc':
        ievent.reply('voice only works on irc bots')
        return

    if len(ievent.args)==0:
        ievent.missing('<nickname>')
        return

    for nick in sets.Set(ievent.args):
        bot.voice(ievent.channel, nick)

cmnds.add('voice', handle_voice, 'OPER')
examples.add('voice', 'give voice to user', 'voice test')
tests.add('voice dunker')
