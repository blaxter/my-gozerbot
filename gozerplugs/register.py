# gozerplugs/plugs/register.py
#
#

__license__ = 'this file is in the public domain'
__gendocfirst__ = ['register-enable', ]

from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.callbacks import callbacks
from gozerbot.users import users
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.plughelp import plughelp
from gozerplugs.throttle import state as throttlestate

plughelp.add('register', 'allow registering of anon users')

cfg = PersistConfig()
cfg.define('enable', 0)
cfg.define('perms', ['USER', ])

def handle_register(bot, ievent):
    if not cfg.get('enable'):
        ievent.reply('register is not enabled')
        return
    if 'OPER' in cfg.get('perms'):
        ievent.reply("can't use OPER permission in register command")
        return
    if not ievent.rest:
        ievent.missing('<username>')
        return
    name = ievent.args[0]
    if users.exist(name):
        ievent.reply('we already have a user with the name %s' % name)
        return
    uh = ievent.userhost
    username = users.getname(uh)
    if username:
        ievent.reply('we already have a user with userhost %s' % uh)
        return
    if users.add(name, [uh, ], perms = cfg.get('perms')):
        throttlestate['level'][uh] = 10
        ievent.reply('%s added to the user database with permission %s' % \
(uh, cfg.get('perms')))
    else:
        ievent.reply('error adding %s (%s) in the user database' % (name, uh))

cmnds.add('register', handle_register, 'ANY')
examples.add('register', 'register yourself to the bot .. this only \
works in jabber', 'register dunker')

def handle_registerenable(bot, ievent):
    cfg.set('enable', 1)
    ievent.reply('register enabled')

cmnds.add('register-enable', handle_registerenable, 'OPER')
examples.add('register-enable', 'enable register command', 'register-enable')

def handle_registerdisable(bot, ievent):
    cfg.set('enable', 0)
    ievent.reply('register disabled')

cmnds.add('register-disable', handle_registerdisable, 'OPER')
examples.add('register-disable', 'disable register command', \
'register-disable')
