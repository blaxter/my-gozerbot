# gozerplugs/plugs/powernick.py
#
#

""" relay log messages to nicks joined on the partyline (DCC CHAT) """

from gozerbot.callbacks import callbacks
from gozerbot.persist.persiststate import PlugState
from gozerbot.commands import cmnds
from gozerbot.users import users
from gozerbot.examples import examples
from gozerbot.partyline import partyline
from gozerbot.plughelp import plughelp
import gozerbot.generic

plughelp.add('powernick', 'plugin used to monitor log messages')

state = PlugState()
state.define('nicks', {}) # username is key


def logcallback(level, description, txt):
    global state
    for nick in state['nicks'].values():
        partyline.say_nick(nick, "[%s] %s" % (description, txt)) 

def init():
    if not logcallback in gozerbot.utils.log.logcallbacks:
        gozerbot.utils.log.logcallbacks.append(logcallback)

def shutdown():
    if logcallback in gozerbot.utils.log.logcallbacks:
        gozerbot.utils.log.logcallbacks.remove(logcallback)

def handle_powernick(bot, ievent):
    global state
    nick = ievent.nick
    if not partyline.is_on(nick):
        ievent.reply('%s is not joined on the partylist .. make a dcc chat\
 connection to the bot' % nick)
        return
    username = users.getname(ievent.userhost)
    state['nicks'][username] = nick
    state.save()
    ievent.reply('powernick set to %s' % nick)

cmnds.add('powernick', handle_powernick, 'OPER')
examples.add('powernick', 'set powernick (gets /msg of bot logs)', 'powernick')

def handle_powernickdel(bot, ievent):
    global state
    username = users.getname(ievent.userhost)
    try:
        del state['nicks'][username]
        state.save()
        ievent.reply('powernick removed')
    except (ValueError, KeyError):
         ievent.reply('no powernick set')
 
cmnds.add('powernick-del', handle_powernickdel, 'OPER')
examples.add('powernick-del', 'remove powernick (gets', 'powernick-del')

def handle_powernicklist(bot, ievent):
    ievent.reply(state['nicks'].values())

cmnds.add('powernick-list', handle_powernicklist, 'OPER')
examples.add('powernick-list', 'show power nicks in use', 'powernick-list')
