# gozerbot/jsonusers.py
#
#

""" bot's users in JSON file. """

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from gozerbot.datadir import datadir
from gozerbot.generic import rlog, stripident, stripidents, \
handle_exception, exceptionmsg, die, stripped
from gozerbot.persist.persist import Persist
from gozerbot.utils.lazydict import LazyDict
from gozerbot.config import config

# basic imports
import re, types, os, time

class JsonUser(LazyDict):

    """ LazyDict representing a user. """

    def __init__(self, name="", userhosts=[], perms=[], permits=[], status=[], email=[], d=None):
        if not d:
            LazyDict.__init__(self)
            self.name = name
            self.userhosts = userhosts
            self.perms = perms
            self.permits = permits
            self.status = status
            self.email = email
        else:
            LazyDict.__init__(self, d)

class JsonUsers(Persist):

    """ class representing all users. """

    def __init__(self, filename, ddir=None):
        self.datadir = ddir or datadir
        Persist.__init__(self, filename)
        if not self.data:
            self.data = {}
        self.users = self.data

    def all(self):

        """ get all users. """

        result = []
        for userdata in self.data.values():
            result.append(JsonUser(d=userdata))
        return result

    ### Misc. Functions
    def size(self):

        """ return nr of users. """

        return len(self.users)

    def names(self):

        """ get names of all users. """

        result = []
        for user in self.all():
            result.append(user.name)
        return result

    def byname(self, name):
        """ return user by name. """ 
        try:
            return JsonUser(d=self.users[name])
        except KeyError:
            return

    def merge(self, name, userhost):
        """ add userhosts to user with name """
        user = self.byname(name)
        if user:
            user.userhosts.append(userhost)
            self.save()
            rlog(10, 'users', "%s merged with %s" % (userhost, name))
            return 1

    def usersearch(self, userhost):
        """ search for users with a userhost like the one specified """
        result = []
        for udata in self.users.values():
            user = JsonUser(d=udata)
            if userhost in user.userhosts:
                 result.append((user.name, user.userhost))
        return result

    def getuser(self, userhost):
        for userdata in self.users.values():
            user = JsonUser(d=userdata)
            if userhost in user.userhosts:
                return user

    ### Check functions
    def exist(self, name):
        """ see if user with <name> exists """
        return self.byname(name)

    def allowed(self, userhost, perms, log=True):
        """ check if user with userhosts is allowed to execute perm command """
        if not type(perms) == types.ListType:
            perms = [perms, ]
        if 'ANY' in perms:
            return 1
        res = None
        user = self.getuser(userhost)
        if not user and log:
            rlog(10, 'users', '%s userhost denied' % userhost)
            return res
        else:
            uperms = set(user.perms)
            sperms = set(perms)
            intersection = sperms.intersection(uperms)
            res = list(intersection) or None
        if not res and log:
            rlog(10, 'users', "%s perm %s denied" % (userhost, str(perms)))
        return res

    def permitted(self, userhost, who, what):
        """ check if (who,what) is in users permit list """
        user = self.getuser(userhost)
        res = None
        if user:
            if '%s %s' % (who, what) in user.permits:
                res = 1
        return res

    def status(self, userhost, status):
        """ check if user with <userhost> has <status> set """
        user = self.getuser(userhost)
        res = None
        if user:
            if status.upper() in user.statuses:
                res = 1
        return res

    def gotuserhost(self, name, userhost):
        """ check if user has userhost """
        user = self.byname(name)
        return userhost in user.userhosts

    def gotperm(self, name, perm):
        """ check if user had permission """
        user = self.byname(name)
        if user:
            return perm.upper() in user.perms

    def gotpermit(self, name, permit):
        """ check if user permits something.  permit is a (who, what) tuple """
        user = self.byname(name)
        if user:
            return '%s %s' % permit in user.permits
        
    def gotstatus(self, name, status):
        """ check if user has status """
        user = self.byname(name)
        return status.upper() in user.statuses

    ### Get Functions
    def getname(self, userhost):
        """ get name of user belonging to <userhost> """
        user = self.getuser(userhost)
        if user:
            return user.name

    def gethosts(self, userhost):
        """ return the userhosts of the user associated with the specified userhost """
        user = self.getuser(userhost)
        if user:
            return user.userhosts
    
    def getemail(self, userhost):
        """ return the email of the specified userhost """
        user = self.getuser(userhost)
        if user:
            if user.email:
                return user.email[0]

    def getperms(self, userhost):
        """ return permission of user"""
        user = self.getuser(userhost)
        if user:
            return user.perms

    def getpermits(self, userhost):
        """ return permits of the specified userhost"""
        user = self.getuser(userhost)
        if user:
            return user.permits

    def getstatuses(self, userhost):
        """ return the list of statuses for the specified userhost """
        user = self.getuser(userhost)
        if user:
            return user.status

    def getuserhosts(self, name):
        """ return the userhosts associated with the specified user """
        user = self.byname(name)
        if user:
            return user.userhosts

    def getuseremail(self, name):
        """ get email of user """
        user = self.byname(name)
        if user:
            if user.email:
                return user.email[0]

    def getuserperms(self, name):
        """ return permission of user"""
        user = self.byname(name)
        if user:
            return user.perms

    def getuserpermits(self, name):
        """ return permits of user"""
        user = self.byname(name)
        if user:
            return user.permits

    def getuserstatuses(self, name):
        """ return the list of statuses for the specified user """
        user = self.byname(name)
        if user:
            return user.status

    def getpermusers(self, perm):
        """ return all users that have the specified perm """
        result = []
        for userdata in self.users.values():
            user = JsonUser(d=userdata)
            if perm.upper() in user.perms:
                result.append(user.name)
        return result

    def getstatususers(self, status):
        """ return all users that have the specified status """
        result = []
        for userdata in self.users.values():
            user = JsonUser(d=userdata)
            if status in user.status:
                result.append(user.name)
        return result

    ### Set Functions
    def setemail(self, name, email):
        """ set email of user """
        user = self.byname(name)
        if user:
            try:
                user.email.remove(email)
            except:
                pass
            user.email.insert(0, email)
            self.save()
            return 1

    ### Add functions
    def add(self, name, userhosts, perms):
        """ add an user """
        if type(userhosts) != types.ListType:
            rlog(10, 'jsonusers', 'i need a list of userhosts')
            return 0
        if not os.path.isdir(self.datadir + os.sep + 'users'):
            os.mkdir(self.datadir + os.sep + 'users')
        if not os.path.isdir(self.datadir + os.sep + 'users' +  os.sep + name):
            os.mkdir(self.datadir + os.sep + 'users' +  os.sep + name)
        user = self.byname(name)
        if not user:
            try:
                newuser = JsonUser(name=name)
                newuser.userhosts.extend(userhosts)
                newuser.perms.extend(perms)
                self.users[name] = newuser
                self.save()
            except Exception, ex:
                rlog(10, 'jsonusers', str(ex))
                return
            rlog(10, 'users', '%s %s %s added to user database' % (name, \
userhosts, perms))
        return 1

    def addemail(self, userhost, email):
        """ add an email address to the userhost """
        user = self.getuser(userhost)
        if user:
            user.email.append(email)
            self.save()
            rlog(10, 'users', '%s (%s) added to email' % (email, userhost))
            return 1

    def addperm(self, userhost, perm):
        """ add the specified perm to the userhost """
        user = self.getuser(userhost)
        if user:
            user.perms.append(perm.upper())
            self.save()
            rlog(10, 'users', '%s perm %s added' % (userhost, perm))
            return 1

    def addpermit(self,  userhost, permit):
        """ add the given (who, what) permit to the given userhost """
        user = self.getuser(userhost)
        if user:
            #p = '%s %s' % permit
            user.permits.append(permit)
            self.save()
            rlog(10, 'users', '%s permit %s added' % (userhost, p))
            return 1

    def addstatus(self, userhost, status):
        """ add status to given userhost"""
        user = self.getuser(userhost)
        if user:
            user.status.append(status.upper())
            self.save()
            rlog(10, 'users', '%s status %s added' % (name, status))
            return 1

    def adduserhost(self, name, userhost):
        """ add userhost """
        user = self.byname(name)
        if not user:
            user = self.users[name] = User(name=name)
        user.userhosts.append(userhost)
        self.save(user)
        rlog(10, 'users', '%s (%s) added to userhosts' % (name, userhost))
        return 1

    def adduseremail(self, name, email):
        """ add email to specified user """
        user = self.byname(name)
        if user:
            user.email.append(email)
            self.save()
            rlog(10, 'users', '%s email %s added' % (name, email))
            return 1

    def adduserperm(self, name, perm):
        """ add permission """
        user = self.byname(name)
        if user:
            perm = perm.upper()
            user.perms.append(perm)
            self.save()
            rlog(10, 'users', '%s perm %s added' % (name, perm))
            return 1

    def adduserpermit(self, name, permit):
        """ add (who, what) permit tuple to sepcified user """
        user = self.byname(name)
        if user:
            p = '%s %s' % permit
            user.permits.append(p)
            self.save()
            rlog(10, 'users', '%s permit %s added' % (name, p))
            return 1

    def adduserstatus(self, name, status):
        """ add status to given user"""
        user = byname(name)
        if user:
            user.status.append(status.upper())
            self.save()
            rlog(10, 'users', '%s status %s added' % (name, status))
            return 1

    def addpermall(self, perm): 
        """ add permission to all users """
        for user in self.users.values():
            user.perms.append(perm.upper())
        self.save()

    ### Delete functions
    def delemail(self, userhost, email):
        """ delete email from userhost """
        user = self.getuser(userhost)
        if user:
            if email in user.emails:
                user.emails.remove(email)
                self.save()
                return 1

    def delperm(self, userhost, perm):
        """ delete perm from userhost """
        user = self.getuser(userhost)
        if user:
            p = perm.upper()
            if p in user.perms:
                user.perms.remove(p)
                self.save()
                return 1

    def delpermit(self, userhost, permit):
        """ delete permit from userhost """
        user = self.getuser(userhost)
        if user:
            p = '%s %s' % permit
            if p in user.permits:
                user.permits.remove(p)
                self.save()
                return 1

    def delstatus(self, userhost, status):
        """ delete status from userhost """
        user = self.getuser(userhost)
        if user:
            st = status.upper()
            if st in user.status:
                user.status.remove(st)
                self.save()
                return 1

    def delete(self, name):
        """ delete user with name """
        del self.users[name]
        self.save()
        return 1

    def deluserhost(self, name, userhost):
        """ delete the userhost entry """
        user = self.byname(name)
        if user:
            if userhost in user.userhosts:
                user.userhosts.remove(userhost)
                self.save()
                rlog(10, 'users', '%s userhost %s deleted' % (name, userhost))
                return 1

    def deluseremail(self, name, email):
        """ delete email """
        user = self.byname(name)
        if user:
            if email in user.email:
                user.email.remove(email)
                self.save()
                rlog(10, 'users', '%s email %s deleted' % (name, email))
                return 1

    def deluserperm(self, name, perm):
        """ delete permission """
        user = self.byname(name)
        if user:
            p = perm.upper()
            if p in user.perms:
                user.perms.remove(p)
                self.save()
                rlog(10, 'users', '%s perm %s deleted' % (name, p))
                return 1

    def deluserpermit(self, name, permit):
        """ delete permit """
        user = self.byname(name)
        if user:
            p = '%s %s' % permit
            if p in user.permits:
                user.permits.remove(p)
                self.save()
                rlog(10, 'users', '%s permit %s deleted' % (name, p))
                return 1

    def deluserstatus(self, name, status):
        """ delete the status from the given user """
        user = self.byname(name)
        if user:
            st = status.upper()
            if st in user.status:
                user.status.remove(status)
                self.save()
                rlog(10, 'users', '%s status %s deleted' % (name, st))
                return 1

    def delallemail(self, name):
        """ Delete all emails for the specified user """
        user = self.byname(name)
        if user:
            user.email = []
            self.save()
            rlog(10, 'users', '%s emails deleted' % (name, ))
            return 1

    def delpermall(self, perm):
        """ delete permission from all users """
        for user in self.users.values():
            if user.name != 'owner':
                del user.perms
        self.save()
        return 1

    def make_owner(self, userhosts):
        """ see if owner already has a user account if not merge otherwise add """
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
