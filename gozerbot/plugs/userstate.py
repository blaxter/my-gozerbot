# gozerplugs/plugs/userstate.py
#
#

""" userstate is stored in gozerdata/userstates """

__gendoclast__ = ['userstate-del', ]

from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.persist.persiststate import UserState
from gozerbot.users import users
from gozerbot.aliases import aliasset
from gozerbot.plughelp import plughelp

plughelp.add('userstate', 'maintain state per user')

def handle_userstate(bot, ievent):
    try:
        (item, value) = ievent.args
    except ValueError:
        item = value = None
    username = users.getname(ievent.userhost)
    userstate = UserState(username)
    if item and value:
        userstate[item] = value
        userstate.save()
    result = []
    for i, j in userstate.data.iteritems():
        result.append("%s=%s" % (i, j))
    if result:
        ievent.reply("userstate of %s: " % username, result, dot=True)
    else:
        ievent.reply('no userstate of %s known' % username)

cmnds.add('userstate', handle_userstate, 'USER')
examples.add('userstate', 'get or set userstate', '1) userstate 2) \
userstate TZ -1')
aliasset('set', 'userstate')

def handle_userstateget(bot, ievent):
    if not ievent.rest:
        ievent.missing('<username>')
        return
    userstate = UserState(ievent.rest)
    result = []
    for i, j in userstate.data.iteritems():
        result.append("%s=%s" % (i, j))
    if result:
        ievent.reply("userstate of %s: " % ievent.rest, result, dot=True)
    else:
        ievent.reply('no userstate of %s known' % ievent.rest)

cmnds.add('userstate-get', handle_userstateget, 'OPER')
examples.add('userstate-get', 'get the userstate of another user', \
'userstate-get dunker')

def handle_userstateset(bot, ievent):
    try:
        (username, item, value) = ievent.args
    except ValueError:
        ievent.missing('<username> <item> <value>')
        return
    userstate = UserState(username)
    userstate[item] = value
    userstate.save()
    ievent.reply('userstate %s set to %s' % (item, value))

cmnds.add('userstate-set', handle_userstateset, 'OPER')
examples.add('userstate-set', 'set userstate variable of another user', \
'userstate-set dunker TZ -1')

def handle_userstatedel(bot, ievent):
    username = None
    try:
        (username, item)  = ievent.args
    except ValueError:
        try:
           item = ievent.args[0]
        except IndexError:
            ievent.missing('[username] <item>')
            return
    if not username:
        username = users.getname(ievent.userhost)
    userstate = UserState(username)
    try:
        del userstate.data[item]
    except KeyError:
        ievent.reply('no such item')
        return
    userstate.save()
    ievent.reply('item %s deleted' % item)

cmnds.add('userstate-del', handle_userstatedel, 'OPER')
examples.add('userstate-del', 'delete userstate variable', \
'1) userstate-del TZ 2) userstate-del dunker TZ')
aliasset('unset', 'userstate-del')
