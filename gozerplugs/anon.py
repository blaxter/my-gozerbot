# gozerplugs/plugs/anon.py
#
#

__license__ = 'this file is in the public domain'
__gendocfirst__ = ['anon-enable', ]
__depend__ = ['throttle', ]

from gozerbot.generic import rlog, jsonstring
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.callbacks import callbacks
from gozerbot.users import users
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.plughelp import plughelp
from gozerbot.tests import tests
from gozerplugs.throttle import state as throttlestate

plughelp.add('anon', 'allow registering of anon users on JOIN')

cfg = PersistConfig()
cfg.define('enable', []) # (bot.name, ievent.channel) pair
cfg.define('perms', ['USER', ])

def anonpre(bot, ievent):
    if 'OPER' not in cfg.get('perms') and \
jsonstring([bot.name, ievent.channel]) in cfg.get('enable'):
        return 1

def anoncb(bot, ievent):
    try:
        username = users.getname(ievent.userhost)
        if not username:
            if users.add(ievent.nick, [ievent.userhost, ], perms = \
cfg.get('perms')):
                throttlestate['level'][ievent.userhost] = 10
                throttlestate.save()
                rlog(100, 'register', 'added %s (%s)' % (ievent.nick, \
ievent.userhost))
                bot.say(ievent.nick, "you have been added to the bots \
user database .. see %shelp for help" % bot.channels[ievent.channel]['cc'])
            else:
                rlog(100, 'register' , "username %s already exists .. can't \
add %s" % (ievent.nick, ievent.userhost))
    except Exception, ex:
        rlog(100, 'register', 'failed to add %s (%s) .. reason: %s' % \
(ievent.nick, ievent.userhost, str(ex)))

callbacks.add('JOIN', anoncb, anonpre, threaded=True)
callbacks.add('Presence', anoncb, anonpre, threaded=True)
tests.add('anon-enable --chan #dunkbots').fakein(':dunker!mekker@127.0.0.1 JOIN #dunkbots').sleep(3).add('delete dunker').add('anon-disable --chan #dunkbots')

def handle_anonenable(bot, ievent):
    cfg.append('enable', jsonstring([bot.name, ievent.channel]))
    ievent.reply('anon enabled on (%s,%s)' % (bot.name, ievent.channel))

cmnds.add('anon-enable', handle_anonenable, 'OPER')
examples.add('anon-enable', 'enable anon register', 'anon-enable')
tests.add('anon-enable', 'anon enabled')

def handle_anondisable(bot, ievent):
    try:
        cfg.remove('enable', jsonstring([bot.name, ievent.channel]))
        ievent.reply('anon disabled on (%s,%s)' % (bot.name, ievent.channel))
    except (KeyError, ValueError):
        ievent.reply('anon is not enabled on (%s,%s)' % (bot.name, \
ievent.channel))

cmnds.add('anon-disable', handle_anondisable, 'OPER')
examples.add('anon-disable', 'disable anon register', 'anon-disable')
tests.add('anon-disable', 'anon disabled')
