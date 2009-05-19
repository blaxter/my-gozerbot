# dbplugs/user.py
#
#

""" users related commands """

__copyright__ = 'this file is in the public domain'

from gozerbot.generic import getwho, stripident, handle_exception
from gozerbot.users import users
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.aliases import aliases, aliasdel
from gozerbot.plughelp import plughelp
from gozerbot.tests import tests

plughelp.add('user', 'manage users')

def handle_whoami(bot, ievent):
    """ user-whoami .. get your username """
    ievent.reply('%s' % users.getname(ievent.userhost))

cmnds.add('user-whoami', handle_whoami, 'USER')
examples.add('user-whoami', 'get your username', 'user-whoami')
aliases.data['whoami'] = 'user-whoami'
tests.add('whoami')

def handle_meet(bot, ievent):
    """ user-meet <nick> .. introduce a new user to the bot """
    try:
        nick = ievent.args[0].lower()
    except IndexError:
        ievent.missing('<nick>')
        return
    if users.exist(nick):
        ievent.reply('there is already a user with username %s' % nick)
        return
    userhost = getwho(bot, nick)
    if not userhost:
        ievent.reply("can't find userhost of %s" % nick)
        return
    username = users.getname(userhost)
    if username:
        ievent.reply('we already have a user with userhost %s (%s)' % \
(userhost, username))
        return
    result = 0
    try:
        result = users.add(nick.lower(), [userhost, ], ['USER', ])
    except Exception, ex:
        ievent.reply('ERROR: %s' % str(ex))
        return
    if result:
        ievent.reply('%s added to user database' % nick)
    else:
        ievent.reply('add failed')

cmnds.add('user-meet', handle_meet, ['OPER', 'MEET'])
examples.add('user-meet', 'user-meet <nick> .. introduce <nick> to the \
bot', 'user-meet dunker')
aliases.data['meet'] = 'user-meet'
tests.add('meet test').add('delete test')

def handle_adduser(bot, ievent):
    """ user-aadd <name> <userhost> .. introduce a new user to the bot """
    try:
        (name, userhost) = ievent.args
    except ValueError:
        ievent.missing('<name> <userhost>')
        return
    username = users.getname(userhost)
    if username:
        ievent.reply('we already have a user with userhost %s (%s)' % \
(userhost, username))
        return
    result = 0
    try:
        result = users.add(name.lower(), [userhost, ], ['USER', ])
    except Exception, ex:
        ievent.reply("ERROR: %s" % str(ex))
        return
    if result:
        ievent.reply('%s added to user database' % name)
    else:
        ievent.reply('add failed')

cmnds.add('user-add', handle_adduser, 'OPER')
examples.add('user-add', 'user-add <name> <userhost> .. add <name> with \
<userhost> to the bot', 'user-add dunker bart@localhost')
tests.add('user-add mtest mekker@test', 'mtest added to user database').add('delete mtest')

def handle_merge(bot, ievent):
    """ user-merge <name> <nick> .. merge the userhost into a already \
        existing user """
    if len(ievent.args) != 2:
        ievent.missing('<name> <nick>')
        return  
    name, nick = ievent.args
    name = name.lower()
    if users.gotperm(name, 'OPER') and not users.allowed(ievent.userhost, \
'OPER'):
        ievent.reply("only OPER perm can merge with OPER user")
        return
    if name == 'owner' and not bot.ownercheck(ievent, "can merge with owner \
user"):
         return 
    if not users.exist(name):
        ievent.reply("we have no user %s" % name)
        return
    userhost = getwho(bot, nick)
    if not userhost:
        ievent.reply("can't find userhost of %s" % nick)
        return
    username = users.getname(userhost)
    if username:
        ievent.reply('we already have a user with userhost %s (%s)' % \
(userhost, username))
        return
    result = 0
    try:
        result = users.merge(name, userhost)
    except Exception, ex:
        ievent.reply("ERROR: %s" % str(ex))
        return
    if result:
        ievent.reply('%s merged' % nick)
    else:
        ievent.reply('merge failed')

cmnds.add('user-merge', handle_merge, ['OPER', 'MEET'])
examples.add('user-merge', 'user-merge <name> <nick> .. merge record with \
<name> with userhost from <nick>', 'merge bart dunker')
aliases.data['merge'] = 'user-merge'
tests.add('user-add mtest mekker@test').add('merge mtest bottest', 'bottest merged').add('delete mtest')

def handle_delete(bot, ievent):
    """ user-del <name> .. remove user """
    if len(ievent.args) == 0:
        ievent.missing('<name>')
        return
    name = ievent.args[0].lower()
    if name == 'owner':
        ievent.reply("can't delete owner")
        return
    result = 0
    try:
        result = users.delete(name)
    except Exception, ex:
        ievent.reply("ERROR: %s" % str(ex))
        return
    if result:
        ievent.reply('%s deleted' % name)
    else:
        ievent.reply('delete of %s failed' % name)

cmnds.add('user-del', handle_delete, 'OPER')
examples.add('user-del', 'user-del <name> .. delete user with <username>' , \
'user-del dunker')
aliases.data['delete'] = 'user-del'
tests.add('user-add mtest mekker@test').add('delete mtest', 'mtest deleted')

def handle_userscan(bot, ievent):
    """ user-scan <txt> .. scan for user """
    try:
        name = ievent.args[0]
    except IndexError:
        ievent.missing('<txt>')
        return
    name = name.lower()
    names = users.names()
    result = []
    for i in names:
        if i.find(name) != -1:
            result.append(i)
    if result:
        ievent.reply("users matching %s: " % name, result, dot=True)
    else:
        ievent.reply('no users matched')
        return

cmnds.add('user-scan', handle_userscan, 'OPER')
examples.add('user-scan', 'user-scan <txt> .. search database for matching \
usernames', 'user-scan dunk')
aliases.data['us'] = 'user-scan'
tests.add('user-add mtest mekker@test').add('user-scan mte', 'mtest').add('delete mtest')

def handle_names(bot, ievent):
    """ user-names .. show registered users """
    ievent.reply("usernames: ", users.names(), dot=True)

cmnds.add('user-names', handle_names, 'OPER')
examples.add('user-names', 'show names of registered users', 'user-names')
aliases.data['names'] = 'user-names'
tests.add('user-add mtest mekker@test').add('user-names', 'mtest').add('delete mtest')

def handle_name(bot, ievent):
    """ user-name .. show name of user giving the command """
    ievent.reply('your name is %s' % users.getname(ievent.userhost))

cmnds.add('user-name', handle_name, 'USER')
examples.add('user-name', 'show name of user giving the commands', \
'user-name')
aliases.data['name'] = 'user-name'
tests.add('user-name')

def handle_getname(bot, ievent):
    """ user-getname <nick> .. fetch name of nick """
    try:
        nick = ievent.args[0]
    except IndexError:
        ievent.missing("<nick>")
        return
    userhost = getwho(bot, nick)
    if not userhost:
        ievent.reply("can't find userhost of %s" % nick)
        return
    name = users.getname(userhost)
    if not name:
        ievent.reply("can't find user for %s" % userhost)
        return
    ievent.reply(name)

cmnds.add('user-getname', handle_getname, 'USER')
examples.add('user-getname', 'user-getname <nick> .. get the name of \
<nick>', 'user-getname dunker')
aliases.data['gn'] = 'user-getname'
aliases.data['getname'] = 'user-getname'
tests.add('user-getname test')

def handle_addperm(bot, ievent):
    """ user-addperm <name> <perm> .. add permission """
    if len(ievent.args) != 2:
        ievent.missing('<name> <perm>')
        return
    name, perm = ievent.args
    perm = perm.upper()
    name = name.lower()
    if not users.exist(name):
        ievent.reply("can't find user %s" % name)
        return
    result = 0
    if users.gotperm(name, perm):
        ievent.reply('%s already has permission %s' % (name, perm))
        return         
    try:
        result = users.adduserperm(name, perm)
    except Exception, ex:
        ievent.reply("ERROR: %s" % str(ex))
        return
    if result:
        ievent.reply('%s perm added' % perm)
    else:
        ievent.reply('perm add failed')

cmnds.add('user-addperm', handle_addperm, 'OPER')
examples.add('user-addperm', 'user-addperm <name> <perm> .. add permissions \
to user <name>', 'user-addperm dunker rss')
aliases.data['setperms'] = 'user-addperm'
aliases.data['addperms'] = 'user-addperm'
tests.add('user-add mtest mekker@test').add('user-addperm mtest mekker', 'MEKKER perm added').add('delete mtest')

def handle_getperms(bot, ievent):
    """ user-getperms <name> .. get permissions of name"""
    try:
        name = ievent.args[0]
    except IndexError:
        ievent.missing('<name>')
        return
    name = name.lower()
    if not users.exist(name):
        ievent.reply("can't find user %s" % name)
        return
    perms = users.getuserperms(name)
    if perms:
        ievent.reply("permissions of %s: " % name, perms, dot=True)
    else:
        ievent.reply('%s has no permissions set' % name)

cmnds.add('user-getperms', handle_getperms, 'OPER')
examples.add('user-getperms', 'user-getperms <name> .. get permissions of \
<name>', 'user-getperms dunker')
aliases.data['getperms'] = 'user-getperms'
tests.add('user-add mtest mekker@test').add('user-addperm mtest mekker').add('user-getperms mtest' , 'MEKKER').add('delete mtest')

def handle_perms(bot, ievent):
    """ user-perms .. get permission of the user given the command """
    if ievent.rest:
        ievent.reply("use getperms to get the permissions of somebody else")
        return
    name = users.getname(ievent.userhost)
    if not name:
         ievent.reply("can't find username for %s" % ievent.userhost)
         return
    perms = users.getuserperms(name)
    if perms:
        ievent.reply("you have permissions: ", perms, dot=True)

cmnds.add('user-perms', handle_perms, 'USER')
examples.add('user-perms', 'get permissions', 'user-perms')
aliases.data['perms'] = 'user-perms'
tests.add('user-perms mtest')

def handle_delperm(bot, ievent):
    """ user-delperm <name> <perm> .. delete permission of name """
    if len(ievent.args) != 2:
        ievent.missing('<name> <perm>')
        return
    name, perm = ievent.args
    perm = perm.upper()
    name = name.lower()
    if not users.exist(name):
        ievent.reply("can't find user %s" % name)
        return
    result = 0
    try:
        result = users.deluserperm(name, perm)
    except Exception, ex:
        ievent.reply("ERROR: %s" % str(ex))
        return
    if result:
        ievent.reply('%s perm removed' % perm)
    else:
        ievent.reply("%s has no %s permission" % (name, perm))
        return

cmnds.add('user-delperm', handle_delperm, 'OPER')
examples.add('user-delperms', 'delete from user <name> permission <perm>', \
'user-delperms dunker rss')
tests.add('user-add mtest mekker@test').add('user-addperm mtest mekker').add('user-delperm mtest mekker' , 'MEKKER').add('delete mtest')

def handle_addstatus(bot, ievent):
    """ user-addstatus <name> <status> .. add status of name """
    if len(ievent.args) != 2:
        ievent.missing('<name> <status>')
        return
    name, status = ievent.args
    status = status.upper()
    name = name.lower()
    if not users.exist(name):
        ievent.reply("can't find user %s" % name)
        return
    result = 0
    if users.gotstatus(name, status):
        ievent.reply('%s already has status %s' % (name, status))
        return
    try:
        result = users.adduserstatus(name, status)
    except Exception, ex:
        ievent.reply("ERROR: %s" % str(ex))
        return
    if result:
        ievent.reply('%s status added' % status)
    else:
        ievent.reply('add failed')

cmnds.add('user-addstatus', handle_addstatus, 'OPER')
examples.add('user-addstatus', 'user-addstatus <name> <status>', \
'user-addstatus dunker #dunkbots')
aliases.data['setstatus'] = 'user-addstatus'
aliases.data['addstatus'] = 'user-addstatus'
tests.add('user-add mtest mekker@test').add('user-addstatus mtest mekker', 'MEKKER status added').add('delete mtest')

def handle_getstatus(bot, ievent):
    """ user-getstatus <name> .. get status of name """
    try:
        name = ievent.args[0]
    except IndexError:
        ievent.missing('<name>')
        return
    name = name.lower()
    if not users.exist(name):
        ievent.reply("can't find user %s" % name)
        return
    status = users.getuserstatuses(name)
    if status:
        ievent.reply("status of %s: " % name, status, dot=True)
    else:
        ievent.reply('%s has no status set' % name)

cmnds.add('user-getstatus', handle_getstatus, 'OPER')
examples.add('user-getstatus', 'user-getstatus <name> .. get status of \
<name>', 'user-getstatus dunker')
aliases.data['getstatus'] = 'user-getstatus'
tests.add('user-add mtest mekker@test').add('user-addstatus mtest mekker', 'MEKKER status added').add('user-getstatus mtest', 'MEKKER').add('delete mtest')

def handle_status(bot, ievent):
    """ user-status .. get status of user given the command """
    status = users.getstatuses(ievent.userhost)
    if status:
        ievent.reply("you have status: ", status, dot=True)
    else:
        ievent.reply('you have no status set')

cmnds.add('user-status', handle_status, 'USER')
examples.add('user-status', 'get status', 'user-status')
aliases.data['status'] = 'user-status'
tests.add('user-status')

def handle_delstatus(bot, ievent):
    """ user-delstatus <name> <status> .. delete status of name """
    if len(ievent.args) != 2:
        ievent.missing('<name> <status>')
        return
    name, status = ievent.args
    status = status.upper()
    name = name.lower()
    if not users.exist(name):
        ievent.reply("can't find user %s" % name)
        return
    result = 0
    try:
        result = users.deluserstatus(name, status)
    except Exception, ex:
        ievent.reply("ERROR: %s" % str(ex))
        return
    if result:
        ievent.reply('%s status deleted' % status)
    else:
        ievent.reply("%s has no %s status" % (name, status))
        return

cmnds.add('user-delstatus', handle_delstatus, 'OPER')
examples.add('user-delstatus', 'user-delstatus <name> <status>', \
'user-delstatus dunker #dunkbots')
aliases.data['delstatus'] = 'user-delstatus'
tests.add('user-add mtest mekker@test').add('user-addstatus mtest mekker').add('user-delstatus mtest mekker', 'MEKKER status deleted').add('delete mtest')

def handle_adduserhost(bot, ievent):
    """ user-adduserhost <name> <userhost> .. add to userhosts of name """ 
    if len(ievent.args) != 2:
        ievent.missing('<name> <userhost>')
        return
    name, userhost = ievent.args
    name = name.lower()
    if name == 'owner' and not bot.ownercheck(ievent, 'can adduserhost to \
owner'):
        return
    if not users.exist(name):
        ievent.reply("can't find user %s" % name)
        return
    if users.gotuserhost(name, userhost):
        ievent.reply('%s already has userhost %s' % (name, userhost))
        return
    result = 0
    try:
        result = users.adduserhost(name, userhost)
    except Exception, ex:
        ievent.reply("ERROR: %s" % str(ex))
        return
    if result:
        ievent.reply('userhost added')
    else:
        ievent.reply('add failed')

cmnds.add('user-adduserhost', handle_adduserhost, 'OPER')
examples.add('user-adduserhost', 'user-adduserhost <name> <userhost>', \
'user-adduserhost dunker bart@%.a2000.nl')
aliases.data['adduserhost'] = 'user-adduserhost'
aliases.data['adduserhosts'] = 'user-adduserhost'
tests.add('user-add mtest mekker@test').add('user-adduserhost mtest mekker2@test', 'userhost added').add('delete mtest')

def handle_deluserhost(bot, ievent):
    """ user-deluserhost <name> <userhost> .. remove from userhosts of name """
    if len(ievent.args) != 2:
        ievent.missing('<name> <userhost>')
        return
    name, userhost = ievent.args
    name = name.lower()
    if name == 'owner'  and not bot.ownercheck(ievent, 'can delete userhosts \
from owner'):
        return 
    if not users.exist(name):
        ievent.reply("can't find user %s" % name)
        return
    result = 0
    try:
        result = users.deluserhost(name, userhost)
    except Exception, ex:
        ievent.reply("ERROR: %s" % str(ex))
        return
    if result:
        ievent.reply('userhost removed')
    else:
        ievent.reply("%s has no %s in userhost list" % (name, \
userhost))
        return  

cmnds.add('user-deluserhost', handle_deluserhost, 'OPER')
examples.add('user-deluserhost', 'user-deluserhost <name> <userhost> .. \
delete from usershosts of <name> userhost <userhost>','user-deluserhost \
dunker bart1@bla.a2000.nl')
aliases.data['deluserhost'] = 'user-deluserhost'
aliases.data['deluserhosts'] = 'user-deluserhost'
tests.add('user-add mtest mekker@test').add('user-adduserhost mtest mekker@test').add('user-deluserhost mtest mekker@test', 'userhost removed').add('delete mtest')

def handle_getuserhosts(bot, ievent):
    """ user-getuserhosts <name> .. get userhosts of name """
    try:
        who = ievent.args[0]
    except IndexError:
        ievent.missing('<name>')
        return
    who = who.lower()
    userhosts = users.getuserhosts(who)
    if userhosts:
        ievent.reply("userhosts of %s: " % who, userhosts, dot=True)
    else:
        ievent.reply("can't find user %s" % who)

cmnds.add('user-getuserhosts', handle_getuserhosts, 'OPER')
examples.add('user-getuserhosts', 'user-getuserhosts <name> .. get \
userhosts of <name>', 'getuserhosts dunker')
aliases.data['getuserhosts'] = 'user-getuserhosts'
tests.add('user-add mtest mekker@test').add('user-adduserhost mtest mekker@test').add('user-getuserhosts mtest', 'mekker@test').add('delete mtest')

def handle_userhosts(bot, ievent):
    """ user-userhosts .. get userhosts of user giving the command """
    userhosts = users.gethosts(ievent.userhost)
    if userhosts:
        ievent.reply("you have userhosts: ", userhosts, dot=True)

cmnds.add('user-userhosts', handle_userhosts, 'USER')
examples.add('user-userhosts', 'get userhosts', 'user-userhosts')
aliases.data['userhosts'] = 'user-userhosts'
tests.add('user-userhosts')

def handle_getemail(bot, ievent):
    """ user-getemail <name> .. get email of name """
    try:
        name = ievent.args[0]
    except IndexError:
        ievent.missing('<name>')
        return
    name = name.lower()
    if not users.exist(name):
        ievent.reply("can't find user %s" % name)
        return
    email = users.getuseremail(name)
    if email:
        ievent.reply(email)
    else:
        ievent.reply('no email set')

cmnds.add('user-getemail', handle_getemail, 'USER')
examples.add('user-getemail', 'user-getemail <name> .. get email from user \
<name>', 'user-getemail dunker')
aliases.data['getemail'] = 'user-getemail'
tests.add('user-add mtest mekker@test').add('user-setemail mtest mekker@test').add('user-getemail mtest', 'mekker@test').add('delete mtest')

def handle_setemail(bot, ievent):
    """ user-setemail <name> .. set email of name """
    try:
        name, email = ievent.args
    except ValueError:
        ievent.missing('<name> <email>')
        return
    if not users.exist(name):
        ievent.reply("can't find user %s" % name)
        return
    users.setemail(name, email)
    ievent.reply('email set')

cmnds.add('user-setemail', handle_setemail, 'OPER')
examples.add('user-setemail', 'user-setemail <name> <email>.. set email of \
user <name>', 'user-setemail dunker bart@gozerbot.org')
aliases.data['setemail'] = 'user-setemail'
tests.add('user-add mtest mekker@test').add('user-setemail mtest mekker@test', 'email set').add('delete mtest')

def handle_email(bot, ievent):
    """ user-email .. show email of user giving the command """
    if len(ievent.args) != 0:
        ievent.reply('use getemail to get the email address of an user .. \
email shows your own mail address')
        return
    email = users.getemail(ievent.userhost)
    if email:
        ievent.reply(email)
    else:
        ievent.reply('no email set')

cmnds.add('user-email', handle_email, 'USER')
examples.add('user-email', 'get email', 'user-email')
aliases.data['email'] = 'user-email'
tests.add('user-setemail owner mekker@mekker').add('user-email', 'mekker@mekker')

def handle_delemail(bot, ievent):
    """ user-delemail .. reset email of user giving the command """
    name = users.getname(ievent.userhost)
    if not name:
        ievent.reply("can't find user for %s" % ievent.userhost)
        return
    result = 0
    try:
        result = users.delallemail(name)
    except Exception, ex:
        ievent.reply("ERROR: %s" % str(ex))
        return
    if result:
        ievent.reply('email removed')
    else:
        ievent.reply('delete failed')

cmnds.add('user-delemail', handle_delemail, 'OPER')
examples.add('user-delemail', 'reset email', 'user-delemail')
aliases.data['delemail'] = 'user-delemail'
tests.add('user-setemail mekker@email').add('user-delemail', 'email removed')

def handle_addpermit(bot, ievent):
    """ user-addpermit <name> <permit> .. add permit to permit list \
        of <name> """
    try:
        who, what = ievent.args
    except ValueError:
        ievent.missing("<name> <permit>")
        return
    if not users.exist(who):
        ievent.reply("can't find username of %s" % who)
        return
    name = users.getname(ievent.userhost)
    if users.gotpermit(name, (who, what)):
        ievent.reply('%s is already allowed to do %s' % (who, what))
        return
    result = 0
    try:
        result = users.adduserpermit(name, (who, what))
    except Exception, ex:
        handle_exception()
        ievent.reply("ERROR: %s" % str(ex))
        return
    if result:
        ievent.reply('permit added')
    else:
        ievent.reply('add failed')

cmnds.add('user-addpermit', handle_addpermit, 'USER')
examples.add('user-addpermit', 'user-addpermit <nick> <what> .. permit \
nick access to <what> .. use setperms to add permissions', \
'user-addpermit dunker todo')
aliasdel('allow')
tests.add('user-add mtest mekker@test').add('user-addpermit mtest todo', 'permit added').add('user-delpermit mtest todo').add('delete mtest')

def handle_permit(bot, ievent):
    """ user-permit .. get permit list of user giving the command """
    if ievent.rest:
        ievent.reply("use the user-addpermit command to allow somebody \
something .. use getname <nick> to get the username of somebody .. this \
command shows what permits you have")
        return
    name = users.getname(ievent.userhost)
    if not name:
        ievent.reply("can't find user for %s" % ievent.userhost)
        return
    permits = users.getuserpermits(name)
    if permits:
        ievent.reply("you permit the following: ", permits, dot=True)
    else:
        ievent.reply("you don't have any permits")

cmnds.add('user-permit', handle_permit, 'USER')
examples.add('user-permit', 'show permit of user giving the command', \
'user-permit')
aliases.data['permit'] = 'user-permit'
tests.add('user-add mtest mekker@test').add('user-addpermit mtest todo', 'permit added').add('user-delpermit mtest todo').add('delete mtest')

def handle_userdelpermit(bot, ievent):
    """ user-delpermit <name> <permit> .. remove (name, permit) from permit 
        list """
    try:
        who, what = ievent.args
    except ValueError:
        ievent.missing("<name> <what>")
        return
    if not users.exist(who):
        ievent.reply("can't find registered name of %s" % who)
        return
    name = users.getname(ievent.userhost)
    if not users.gotpermit(name, (who, what)):
        ievent.reply('%s is already not allowed to do %s' % (who, what))
        return
    result = 0
    try:
        result = users.deluserpermit(name, (who, what))
    except Exception, ex:
        ievent.reply("ERROR: %s" % str(ex))
        return
    if result:
        ievent.reply('%s denied' % what)
    else:
        ievent.reply('delete failed')

cmnds.add('user-delpermit', handle_userdelpermit, 'USER')
examples.add('user-delpermit', 'user-delpermit <name> <permit>', \
'user-delpermit dunker todo')
aliasdel('deny')
tests.add('user-add mtest mekker@test').add('user-addpermit mtest todo', 'permit added').add('user-delpermit mtest todo').add('delete mtest')

def handle_check(bot, ievent):
    """ user-check <nick> .. get user data of <nick> """
    try:
        nick = ievent.args[0]
    except IndexError:
        ievent.missing('<nick>')
        return
    userhost = getwho(bot, nick)
    if not userhost:
        ievent.reply("can't find userhost of %s" % nick)
        return
    name = users.getname(userhost)
    if not name:
        ievent.reply("can't find user")
        return
    userhosts = users.getuserhosts(name)
    perms = users.getuserperms(name)
    email = users.getuseremail(name)
    permits = users.getuserpermits(name)
    status = users.getuserstatuses(name)
    ievent.reply('userrecord of %s = userhosts: %s perms: %s email: %s \
permits: %s status: %s' % (name, str(userhosts), str(perms), \
str(email), str(permits), str(status)))

cmnds.add('user-check', handle_check, 'OPER')
examples.add('user-check', 'user-check <nick>', 'user-check dunker')
aliases.data['check'] = 'user-check'
tests.add('user-add mtest mekker@test').add('user-check mtest', 'mekker@test').add('delete mtest')

def handle_show(bot, ievent):
    """ user-show <name> .. get data of <name> """
    try:
        name = ievent.args[0]
    except IndexError:
        ievent.missing('<name>')
        return
    name = name.lower()
    if not users.exist(name):
        ievent.reply("can't find user %s" % name)
        return
    userhosts = users.getuserhosts(name)
    perms = users.getuserperms(name)
    email = users.getuseremail(name)
    permits = users.getuserpermits(name)
    status = users.getuserstatuses(name)
    ievent.reply('userrecord of %s = userhosts: %s perms: %s email: %s \
permits: %s status: %s' % (name, str(userhosts), str(perms), \
str(email), str(permits), str(status)))

cmnds.add('user-show', handle_show, 'OPER')
examples.add('user-show', 'user-show <name> .. show data of <name>', \
'user-show dunker')
tests.add('user-add mtest mekker@test').add('user-show mtest', 'mekker@test').add("delete mtest")

def handle_match(bot, ievent):
    """ user-match <userhost> .. get data of <userhost> """
    try:
        userhost = ievent.args[0]
    except IndexError:
        ievent.missing('<userhost>')
        return
    name = users.getname(userhost)
    if not name:
        ievent.reply("can't find user with userhost %s" % userhost)
        return
    userhosts = users.getuserhosts(name)
    perms = users.getuserperms(name)
    email = users.getuseremail(name)
    permits = users.getuserpermits(name)
    status = users.getuserstatuses(name)
    ievent.reply('userrecord of %s = userhosts: %s perms: %s email: %s \
permits: %s status: %s' % (name, str(userhosts), str(perms), \
str(email), str(permits), str(status)))

cmnds.add('user-match', handle_match, ['USER', 'OPER'])
examples.add('user-match', 'user-match <userhost>', 'user-match test@test')
aliases.data['match'] = 'user-match'
tests.add('user-add mtest mekker@test').add('user-match mekker@test', 'mekker@test').add("delete mtest")

def handle_getuserstatus(bot, ievent):
    """ user-allstatus <status> .. list users with status <status> """
    try:
        status = ievent.args[0].upper()
    except IndexError:
        ievent.missing('<status>')
        return
    result = users.getstatususers(status)
    if result:
        ievent.reply("users with %s status: " % status, result, dot=True)
    else:
        ievent.reply("no users with %s status found" % status)
    return

cmnds.add('user-allstatus', handle_getuserstatus, 'OPER')
examples.add('user-allstatus', 'user-allstatus <status> .. get all users \
with <status> status', 'user-allstatus #dunkbots')
tests.add('user-allstatus')

def handle_getuserperm(bot, ievent):
    """ user-allperm <perm> .. list users with permission <perm> """
    try:
        perm = ievent.args[0].upper()
    except IndexError:
        ievent.missing('<perm>')
        return
    result = users.getpermusers(perm)
    if result:
        ievent.reply('users with %s permission: ' % perm, result, dot=True)
    else:
        ievent.reply("no users with %s permission found" % perm)
    return

cmnds.add('user-allperm', handle_getuserperm, 'OPER')
examples.add('user-allperm', 'user-allperm <perm> .. get users with \
<perm> permission', 'user-allperm rss')
tests.add('user-allperm OPER')

def handle_usersearch(bot, ievent):
    """ search for user matching given userhost """
    try:
        what = ievent.args[0]
    except IndexError:
        ievent.missing('<what>')
        return
    result = users.usersearch(what)
    if result:
        res = ["(%s) %s" % u for u in result]
        ievent.reply('users matching %s: ' % what, res, dot=True)
    else:
        ievent.reply('no userhost matching %s found' % what)

cmnds.add('user-search', handle_usersearch, 'OPER')
examples.add('user-search', 'search users userhosts', 'user-search gozerbot')
tests.add('user-search test', 'test')

def handle_addpermall(bot, ievent):
    """ user-addpermall <perm> .. add permission to all users """
    try:
        perm = ievent.args[0].upper()
    except IndexError:
        ievent.missing('<perm>')
        return
    if perm == 'OPER':
        ievent.reply("can't add OPER permissions to all")
        return
    users.addpermall(perm)
    ievent.reply('%s perm added' % perm)

cmnds.add('user-addpermall', handle_addpermall, 'OPER')
examples.add('user-addpermall', 'user-addpermall <perm> .. add <permission> \
to all users', 'addpermsall USER')
tests.add('user-addpermall blabla', 'BLABLA perm added').add('user-delpermall blabla')

def handle_delpermall(bot, ievent):
    """ user-delpermall <perm> .. delete permission from all users """
    try:
        perm = ievent.args[0].upper()
    except IndexError:
        ievent.missing('<perm>')
        return
    if perm == 'OPER':
        ievent.reply("can't delete OPER permissions from all")
        return
    users.delpermall(perm)
    ievent.reply('%s perm deleted' % perm)

cmnds.add('user-delpermall', handle_delpermall, 'OPER')
examples.add('user-delpermall', 'user-delpermall <perm> .. delete \
<permission> from all users', 'delpermsall BLA')
tests.add('user-addpermall blabla').add('user-delpermall blabla', 'BLABLA perm deleted')

