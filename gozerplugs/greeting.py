# plugs/greeting.py
#
#

""" say greet message when user joins """

__copyright__ = 'this file is in the public domain'

from gozerbot.utils.generic import convertpickle
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.persist.pdol import Pdol
from gozerbot.datadir import datadir
from gozerbot.users import users
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.callbacks import callbacks
from gozerbot.plughelp import plughelp
import random, os

plughelp.add('greeting', 'the greeting plugin allows users to set messages \
to be said when they join a channel')

## UPGRADE PART

def upgrade():
    convertpickle(datadir + os.sep + 'old' + os.sep + 'greetings', \
datadir + os.sep + 'plugs' + os.sep + 'greeting' + os.sep + 'greetings')

cfg = PersistConfig()
cfg.define('enable', [])

greetings = None

def init():
    """ init the greeting plugin """
    global greetings
    greetings = Pdol(datadir + os.sep + 'plugs' + os.sep + 'greeting' + \
os.sep + 'greetings')
    if not greetings.data:
        upgrade()
        greetings = Pdol(datadir + os.sep + 'plugs' + os.sep + 'greeting' + \
os.sep + 'greetings')
    return 1

def greetingtest(bot, ievent):
    """ check if greeting callback should be called """
    if greetings and ievent.channel in cfg.get('enable'):
        return 1

def greetingcallback(bot, ievent):
    """ do the greeting """
    username = users.getname(ievent.userhost)
    try:
        greetingslist = greetings[username]
        if greetingslist:
            ievent.reply(random.choice(greetingslist))
    except KeyError:
        pass

callbacks.add('JOIN', greetingcallback, greetingtest)

def handle_greetingadd(bot, ievent):
    """ add greetings txt """
    if not greetings:
        ievent.reply('the greet plugin is not properly initialised')
    if not ievent.rest:
        ievent.missing('<txt>')
        return
    username = users.getname(ievent.userhost)
    greetings.add(username, ievent.rest)
    greetings.save()
    ievent.reply('greeting message added')

cmnds.add('greeting-add', handle_greetingadd, 'USER')
examples.add('greeting-add', "add greeting message", 'greeting-add yooo dudes')

def handle_greetingdel(bot, ievent):
    """ delete greetings txt """
    if not greetings:
        ievent.reply('the greet plugin is not properly initialised')
        return
    try:
        nr = int(ievent.args[0])
    except (IndexError, ValueError):
        ievent.missing('<nr>')
        return
    username = users.getname(ievent.userhost)
    try:
        del greetings.data[username][nr]
    except (IndexError, KeyError):
        ievent.reply("can't delete greeting %s" % nr)
        return
    greetings.save()
    ievent.reply('greeting message %s removed' % nr)

cmnds.add('greeting-del', handle_greetingdel, 'USER')
examples.add('greeting-del', "delete greeting message", 'greeting-delete 1')

def handle_greetinglist(bot, ievent):
    """ list the greetings list of an user """
    if not greetings:
        ievent.reply('the greet plugin is not properly initialised')
        return
    username = users.getname(ievent.userhost)
    result = greetings.get(username)
    if result:
        ievent.reply("greetings: ", result, nr=0)
    else:
        ievent.reply('no greetings set')

cmnds.add('greeting-list', handle_greetinglist, 'USER')
examples.add('greeting-list', 'show greetings of user', 'greeting-list')
