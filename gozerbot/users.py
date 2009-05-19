# gozerbot/users.py
#
#

""" bot's users """

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from gozerbot.datadir import datadir
from gozerbot.generic import rlog, stripident, stripidents, \
handle_exception, exceptionmsg, die, stripped
from gozerbot.persist.persist import Persist
from gozerbot.config import config
from gozerbot.jsonusers import JsonUsers

# basic imports
import re, types, os, time

# see if we need to use the database or use the jsonusers
if not config['nodb']:
    from gozerbot.database.alchemy import create_session, \
    UserHost, User, Perms, Statuses, query, getuser, byname, dblocked, trans
else:
    def trans(func, *args, **kwargs):
        def transaction(*args, **kwargs):
            func(*args, **kwargs)
        return transaction


class Dbusers(object):

    """ users class """

    def __init__(self, ddir=None):
        self.datadir = ddir or datadir

    ### Misc. Functions
    def size(self):

        """ return nr of users. """

        return query(User).count()

    def names(self):

        """ get names of all users. """

        return [n.name for n in query(User).all()]

    @trans
    def merge(self, session, name, userhost):

        """ add userhosts to user with name. """

        user = byname(name)
        if user:
            if name not in user.userhosts:
                user.userhosts.append(userhost)
                session.refresh(user)
                rlog(10, 'users', "%s merged with %s" % (userhost, name))
                return 1

    def usersearch(self, userhost):

        """ search for users with a userhost like the one specified. """

        n = query(UserHost).filter(UserHost.userhost.like('%%%s%%' % userhost)).all()
        return [(u.name, u.userhost) for u in n]

    ### Check functions
    def exist(self, name):

        """ see if user with <name> exists. """

        return byname(name)

    def allowed(self, userhost, perms, log=True):

        """ check if user with userhosts is allowed to execute perm command. """

        if not type(perms) == types.ListType:
            perms = [perms, ]
        if 'ANY' in perms:
            return 1
        res = None
        user = getuser(userhost)

        if not user:
            if log:
                rlog(10, 'users', '%s userhost denied' % userhost)
            return res
        else:
            uperms = set(user.perms)
            sperms = set(perms)
            intersection = sperms.intersection(uperms)
            res = list(intersection) or None

        if not res and log:
            rlog(10, 'users', "%s perm %s denied" % (userhost, str(perms)))

        if res and log:
            rlog(10, 'users', 'allowed %s %s perm' % (userhost, str(perms)))

        return res

    def permitted(self, userhost, who, what):

        """ check if (who,what) is in users permit list. """

        user = getuser(userhost)
        res = None
        if user:
            if '%s %s' % (who, what) in user.permits:
                res = 1
        return res

    def status(self, userhost, status):

        """ check if user with <userhost> has <status> set. """

        user = getuser(userhost)
        res = None
        if user:
            if status.upper() in user.statuses:
                res = 1
        return res

    def gotuserhost(self, name, userhost):

        """ check if user has userhost. """

        user = byname(name)
        return userhost in user.userhosts

    def gotperm(self, name, perm):

        """ check if user had permission. """

        user = byname(name)
        if user:
            return perm.upper() in user.perms

    def gotpermit(self, name, permit):

        """ check if user permits something.  permit is a [who, what] list. """

        user = byname(name)
        if user:
            return '%s %s' % permit in user.permits
        
    def gotstatus(self, name, status):

        """ check if user has status. """

        user = byname(name)
        return status.upper() in user.statuses

    ### Get Functions
    def getname(self, userhost):

        """ get name of user belonging to <userhost>. """

        user = getuser(userhost)
        if user:
            return user.name

    def gethosts(self, userhost):

        """ return the userhosts of the user associated with the specified userhost. """

        user = getuser(userhost)
        if user:
            return user.userhosts
    
    def getemail(self, userhost):

        """ return the email of the specified userhost. """

        user = getuser(userhost)
        if user:
            if user.email:
                return user.email[0]

    def getperms(self, userhost):

        """ return permissions of user."""

        user = getuser(userhost)
        if user:
            return user.perms

    def getpermits(self, userhost):

        """ return permits of the specified userhost."""

        user = getuser(userhost)
        if user:
            return user.permits

    def getstatuses(self, userhost):

        """ return the list of statuses for the specified userhost. """

        user = getuser(userhost)
        if user:
            return user.statuses

    def getuserhosts(self, name):

        """ return the userhosts associated with the specified user. """

        user = byname(name)
        if user:
            return user.userhosts

    def getuseremail(self, name):

        """ get email of user. """

        user = byname(name)
        if user:
            if user.email:
                return user.email[0]

    def getuserperms(self, name):

        """ return permission of user. """

        user = byname(name)
        if user:
            return user.perms

    def getuserpermits(self, name):
 
        """ return permits of user. """

        user = byname(name)
        if user:
            return user.permits

    def getuserstatuses(self, name):

        """ return the list of statuses for the specified user. """

        user = byname(name)
        if user:
            return user.statuses

    def getpermusers(self, perm):

        """ return all users that have the specified perm. """

        n = query(Perms).filter(Perms.perm==perm.upper()).all()
        return [user.name for user in n]

    def getstatususers(self, status):

        """ return all users that have the specified status. """

        n = query(Statuses).filter(Statuses.status==status.upper()).all()
        return [user.name for user in n]

    ### Set Functions
    @trans
    def setemail(self, session, name, email):

        """ set email of user. """

        user = byname(name, session)

        if user:
            try:
                user.email.remove(email)
            except:
                pass
            user.email.insert(0, email)
            session.refresh(user)
            return 1

    ### Add functions
    @trans
    def add(self, session, name, userhosts, perms):

        """ add an user. """

        if type(userhosts) != types.ListType:
            rlog(10, 'users', 'i need a list of userhosts')
            return 0

        if not os.path.isdir(self.datadir + os.sep + 'users'):
            os.mkdir(self.datadir + os.sep + 'users')

        if not os.path.isdir(self.datadir + os.sep + 'users' +  os.sep + name):
            os.mkdir(self.datadir + os.sep + 'users' +  os.sep + name)

        user = byname(name, session)
        if not user:
            try:
                newuser = User(name=name)
                newuser.userhosts.extend(userhosts)
                newuser.perms.extend(perms)
                session.add(newuser)
                session.commit()
            except Exception, ex:
                rlog(10, 'users', str(ex))
                return
            rlog(10, 'users', '%s %s %s added to user database' % (name, userhosts, perms))

        return 1

    @trans
    def addemail(self, session, userhost, email):

        """ add an email address to the userhost. """

        user = getuser(userhost, session)
        if user:
            user.email.append(email)
            rlog(10, 'users', '%s (%s) added to email' % (email, userhost))
            return 1

    @trans
    def addperm(self, session, userhost, perm):

        """ add the specified perm to the userhost. """

        user = getuser(userhost, session)
        if user:
            user.perms.append(perm.upper())
            rlog(10, 'users', '%s perm %s added' % (userhost, perm))
            return 1

    @trans
    def addpermit(self, session, userhost, permit):

        """ add the given [who, what] permit to the given userhost. """

        user = getuser(userhost, session)
        if user:
            p = '%s %s' % permit
            user.permits.append(p)
            rlog(10, 'users', '%s permit %s added' % (userhost, p))
            return 1

    @trans
    def addstatus(self, session, userhost, status):

        """ add status to given userhost. """

        user = getuser(userhost, session)
        if user:
            user.statuses.append(status.upper())
            rlog(10, 'users', '%s status %s added' % (name, status))
            return 1

    @trans
    def adduserhost(self, session, name, userhost):

        """ add userhost. """

        user = byname(name, session)
        if not user:
            user = User(name=name)
            session.add(user)
            session.commit()
        user.userhosts.append(userhost)
        rlog(10, 'users', '%s (%s) added to userhosts' % (name, userhost))
        return 1

    @trans
    def adduseremail(self, session, name, email):

        """ add email to specified user. """

        user = byname(name, session)
        if user:
            user.email.append(email)
            rlog(10, 'users', '%s email %s added' % (name, email))
            return 1

    @trans
    def adduserperm(self, session, name, perm):

        """ add permission. """

        user = byname(name, session)
        if user:
            perm = perm.upper()
            user.perms.append(perm)
            rlog(10, 'users', '%s perm %s added' % (name, perm))
            return 1

    @trans
    def adduserpermit(self, session, name, permit):

        """ add (who, what) permit tuple to sepcified user. """

        user = byname(name, session)
        if user:
            p = '%s %s' % permit
            user.permits.append(p)
            rlog(10, 'users', '%s permit %s added' % (name, p))
            return 1

    @trans
    def adduserstatus(self, session, name, status):

        """ add status to given user. """

        user = byname(name, session)
        if user:
            user.statuses.append(status.upper())
            session.commit()
            rlog(10, 'users', '%s status %s added' % (name, status))
            return 1

    @trans
    def addpermall(self, session, perm): 

        """ add permission to all users. """

        users = query(User, session).all()
        if users:
            for user in users:
                user.perms.append(perm.upper())
                session.refresh(user)

    ### Delete functions
    @trans
    def delemail(self, session, userhost, email):

        """ delete email from userhost. """

        user = getuser(userhost, session)
        if user:
            if email in user.emails:
                user.emails.remove(email)
                return 1

    @trans
    def delperm(self, session, userhost, perm):

        """ delete perm from userhost. """

        user = getuser(userhost, session)
        if user:
            p = perm.upper()
            if p in user.perms:
                user.perms.remove(p)
                return 1

    @trans
    def delpermit(self, session, userhost, permit):

        """ delete permit from userhost. """

        user = getuser(userhost, session)
        if user:
            p = '%s %s' % permit
            if p in user.permits:
                user.permits.remove(p)
                return 1

    @trans
    def delstatus(self, session, userhost, status):

        """ delete status from userhost. """

        user = getuser(userhost, session)
        if user:
            st = status.upper()
            if st in user.statuses:
                user.statuses.remove(st)
                return 1

    @trans
    def delete(self, session, name):

        """ delete user with name. """

        user = byname(name, session)
        if user:
            session.delete(user)
            session.commit()
            return 1

    @trans
    def deluserhost(self, session, name, userhost):

        """ delete the userhost entry. """

        user = byname(name, session)
        if user:
            if userhost in user.userhosts:
                user.userhosts.remove(userhost)
                rlog(10, 'users', '%s userhost %s deleted' % (name, userhost))
                return 1

    @trans
    def deluseremail(self, session, name, email):

        """ delete email.  """

        user = byname(name, session)
        if user:
            if email in user.email:
                user.email.remove(email)
                session.refresh(user)
                rlog(10, 'users', '%s email %s deleted' % (name, email))
                return 1

    @trans
    def deluserperm(self, session, name, perm):

        """ delete permission. """

        user = byname(name, session)
        if user:
            p = perm.upper()
            if p in user.perms:
                user.perms.remove(p)
                rlog(10, 'users', '%s perm %s deleted' % (name, p))
                return 1

    @trans
    def deluserpermit(self, session, name, permit):

        """ delete permit. """

        user = byname(name, session)
        if user:
            p = '%s %s' % permit
            if p in user.permits:
                user.permits.remove(p)
                rlog(10, 'users', '%s permit %s deleted' % (name, p))
                return 1

    @trans
    def deluserstatus(self, session, name, status):

        """ delete the status from the given user. """

        user = byname(name, session)
        if user:
            st = status.upper()
            if st in user.statuses:
                user.statuses.remove(status)
                rlog(10, 'users', '%s status %s deleted' % (name, st))
                return 1

    @trans
    def delallemail(self, session, name):

        """ Delete all emails for the specified user. """

        user = byname(name, session)
        if user:
            user.email = []
            rlog(10, 'users', '%s emails deleted' % (name, ))
            return 1

    @trans
    def delpermall(self, session, perm):

        """ delete permission from all users. """

        users = query(User, session).all()
        for user in users:
            if user.name != 'owner':
                try:
                    user.perms.remove(perm)
                    session.refresh(user)
                except ValueError:
                    pass
        return 1

    def make_owner(self, userhosts):

        """ see if owner already has a user account if not merge otherwise add. """

        assert(userhosts)
        owner = []

        if type(userhosts) != types.ListType:
            owner.append(userhosts)
        else:
            owner = userhosts

        for userhost in owner:
            username = self.getname(unicode(userhost))
            if not username:
                if not self.merge('owner', unicode(userhost)):
                    self.add('owner', [unicode(userhost), ], ['USER', 'OPER'])

# default to database
if not config['nodb']:
    users = Dbusers()
else:
    # otheriwse use json users
    users = JsonUsers(datadir + os.sep + (config['jsonuser'] or 'users.json'))
