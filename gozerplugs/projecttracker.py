# gozerplugs/projecttracker.py
#
# Hans van Kranenburg <hans@knorrie.org>


""" track hours spent working on projects

Persitent data is stored in a gozerbot Persist object, 'projects'

user is owner of a project:
   projects.data[username][project] exists
   contrib.data[username][project] MUST NOT exist

   projects.data[username][project]['hours'] may exist
       dict: {user: total hours, ...}
   projects.data[username][project]['desc'] may exist
       string: project description
   projects.data[username][project]['share'] may exist
       list: other contributing users

user contributes to a project of another user:
   contrib.data[username][project] exists
       string: project owner username
   projects.data[username][project] MUST NOT exist

"""

__copyright__ = 'this file is in the public domain'
__gendocfirst__ = ['pt-add', ]
__gendoclast__ = ['pt-del', ]

from gozerbot.utils.generic import convertpickle
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.users import users
from gozerbot.datadir import datadir
from gozerbot.persist.persist import PlugPersist
from gozerbot.plughelp import plughelp

plughelp.add('projecttracker', 'track hours spent working on projects')

## UPGRADE PART

def upgrade():
    convertpickle(datadir + os.sep + 'old' + os.sep + 'pt-projects', \
datadir + os.sep + 'plugs' + os.sep + 'projecttracker' + os.sep + 'pt-projects')
    convertpickle(datadir + os.sep + 'old' + os.sep + 'pt-contrib', \
datadir + os.sep + 'plugs' + os.sep + 'projecttracker' + os.sep + 'pt-contrib')

## END UPGRADE PART

import os

projects = PlugPersist('pt-projects')
contrib  = PlugPersist('pt-contrib') 
if not projects.data:
    projects = PlugPersist('pt-projects')
    if not projects.data:
        projects.data = {}
if not contrib.data:
    contrib.data = {}

def size():
    """ return number of projects """
    size = 0
    for userprojects in projects.data:
        size += len(userprojects)
    return size

#
# projects we pwn
#

def addproject(username, project, desc):
    """ add project to projects of username """
    if not projects.data.has_key(username):
        projects.data[username] = {}
    if not projects.data[username].has_key(project):
        projects.data[username][project] = {}
    if desc:
        projects.data[username][project]['desc'] = desc
    projects.save()

def hasproject(username, project):
    """ look if this user owns a project """
    if projects.data.has_key(username) and \
    projects.data[username].has_key(project):
        return True
    return False

def delproject(username, project):
    """ delete a project """
    try:
        if projects.data[username].has_key(project):
            # delete contributions
            if projects.data[username][project].has_key('share'):
                for otheruser in \
                projects.data[username][project]['share']:
                    try:
                        del contrib.data[otheruser][project]
                    except KeyError:
                        pass
            # delete project
            del projects.data[username][project]
    except KeyError:
        pass
    projects.save()
    contrib.save()

def getprojects(username):
    """ return projects owned by username """
    try:
        return projects.data[username].keys()
    except KeyError:
        return []

def setdesc(username, project, desc):
    """ alter project description """
    try:
        projects.data[username][project]['desc'] = desc
	projects.save()
    except KeyError:
        pass

def getdesc(username, project):
    """ return description of project """
    try:
        return projects.data[username][project]['desc']
    except KeyError:
        return None

#
# project sharing
#

def addshare(username, project, otheruser):
    """ share our project with another user
    make sure that 1) we own the project and 2) the other user has
    no project with this name and does not contribute to a project
    with the same name before calling this function    
    """
    # add other user to the sharelist of the project
    if not projects.data[username][project].has_key('share'):
        projects.data[username][project]['share'] = [otheruser, ]
    else:
        projects.data[username][project]['share'].append(otheruser)
    projects.save()
    # add project and project owner to otherusers contrib-list
    if not contrib.data.has_key(otheruser):
        contrib.data[otheruser] = {project: username}
    else:
        contrib.data[otheruser][project] = username
    contrib.save()


def delshare(username, project, otheruser):
    """ stop sharing our project with another user """
    # remove other user from the sharelist
    try:
        projects.data[username][project]['share'].remove(otheruser)
        projects.save()
    except KeyError:
        pass
    try:
        del contrib.data[otheruser][project]
        contrib.save()
    except KeyError:
        pass

def hascontrib(username, project):
    """ does this user contribute to a project with this name? """
    try:
        return contrib.data[username].has_key(project)
    except KeyError:
        return False

def getowner(username, project):
    """ get owner of a project we contribute to """
    if hascontrib(username, project):
        return contrib.data[username][project]
    return None

def getcontrib(username):
    """ get names of projects we contribute to """
    try:
        return contrib.data[username].keys()
    except KeyError:
        return []

def delcontrib(username, project):
    """ stop contributing to a project of someone else """
    if hascontrib(username, project):
        owner = getowner(username, project)
        delshare(owner, project, username)

def getsharelist(username, project):
    """ get users sharing a project with """
    if projects.data[username][project].has_key('share'):
        return projects.data[username][project]['share']
    else:
        return []

#
# do some work... actually ;]
#

def addhours(owner, project, username, hours):
    """ add work hours to a project """

    if not projects.data[owner][project].has_key('hours'):
        projects.data[owner][project]['hours'] = {}
    if not projects.data[owner][project]['hours'].has_key(username):
        projects.data[owner][project]['hours'][username] = hours
    else:
        projects.data[owner][project]['hours'][username] += hours
    projects.save()
    return projects.data[owner][project]['hours'][username]

def gethourslist(username, project):
    """ get list of contributors and hours of work
        for a project
    """
    result = []
    if hasproject(username, project):
        owner = username
    elif hascontrib(username, project):
        owner = getowner(username, project)
    else:
        result.append("unknown project %s" % project)
        return result
    if projects.data[owner][project].has_key('hours'):
        # (h)ours(l)ist
        hl = projects.data[owner][project]['hours']
        if hl:
            # (c)ontributor to the project
            for c in hl:
                if hl[c] != 0:
                    result.append('%s (%s)' % (c, hl[c]))
    if not result:
        result.append("no work done yet")
    return result

#
# command handlers
#

def handle_projectadd(bot, ievent):
    """ pt-add <projectname> <description> .. add project """
    if not ievent.rest:
        ievent.missing('<projectname> [<description>]')
        return
    username = users.getname(ievent.userhost)
    try:
        project, desc = ievent.rest.split(' ', 1)
    except ValueError:
        project = ievent.rest
        desc = None
    project = project.strip().lower()
    if hasproject(username, project) or hascontrib(username, project):
        ievent.reply('project %s already exists' % project)
        return
    if desc:
        desc = desc.strip()
    addproject(username, project, desc)
    ievent.reply('project %s added' % (project))

cmnds.add('pt-add', handle_projectadd, 'USER')
examples.add('pt-add', 'pt-add <projectname> [<description>] .. \
add a project to the project tracker', 'pt-add gc Gozerbot coden ;]')

def handle_projectlist(bot, ievent):
    """ show available projects """
    username = users.getname(ievent.userhost)
    result = []
    l = getprojects(username)
    for project in l:
        desc = getdesc(username, project)
        if desc:
            result.append('%s (%s)' % (desc, project))
        else:
            result.append(project)
    l = getcontrib(username)
    for project in l:
        owner = getowner(username, project)
        desc = getdesc(owner, project)
        if desc:
            result.append('%s (%s, owner=%s)' % (desc, project, \
            owner))
        else:
            result.append('%s, owner=%s' % (project, owner))
    if result:
        ievent.reply('', result, dot=True)
    else:
        ievent.reply('no projects found')

cmnds.add('pt-list', handle_projectlist, 'USER')
examples.add('pt-list', 'list available projects', 'pt-list')

def handle_projectdel(bot, ievent):
    """ delete a project or stop contributing to it """
    try:
        project = ievent.rest.strip().lower()
    except ValueError:
        ievent.missing('<projectname>')
        return
    username = users.getname(ievent.userhost)
    if hasproject(username, project):
        delproject(username, project)
        ievent.reply('project %s deleted' % (project))
    elif hascontrib(username, project):
        delcontrib(username, project)
        ievent.reply('no longer contributing to %s' % (project))
    else:
        ievent.reply('no project %s' % project)

cmnds.add('pt-del', handle_projectdel, 'USER')
examples.add('pt-del', 'delete a project from the project tracker or \
stop contibuting to it', 'pt-del mekker')

def handle_addhours(bot, ievent):
    """ add hours to a project """
    username = users.getname(ievent.userhost)
    try:
        project, rest = ievent.rest.split(' ', 1)
    except ValueError:
        ievent.missing('<projectname> <hours> [<comment>]')
        return
    project = project.strip().lower()

    if hasproject(username, project):
        owner = username
    elif hascontrib(username, project):
        owner = getowner(username, project)
    else:
        ievent.reply('no project %s' % project)
        return
    try:
        hours, comment = rest.split(' ', 1)
    except ValueError:
        hours = rest
        comment = ''
    try:
        hours = float(hours)
    except ValueError:
        ievent.reply('%s is not a number' % hours)
        return
    total = addhours(owner, project, username, hours)
    desc = getdesc(owner, project) or project
#    h = 'hours'
#    if abs(hours) == 1:
#        h = 'hour'
#    if hours < 0:
#        ievent.reply('removed %s %s from %s' % (hours, h, project))
#        return
#    ievent.reply('added %s %s to %s' % (hours, h, project))
     
    ievent.reply('hours spent on %s is now: %s' % (desc, total))

cmnds.add('pt', handle_addhours, 'USER')
examples.add('pt', 'track time spent on a project', 'pt gc 4')

def handle_report(bot, ievent):
    """ display project report """
    username = users.getname(ievent.userhost)
    if not ievent.rest:
        result = []
        l = getprojects(username)
        for project in l:
            desc = getdesc(username, project) or project
            report = gethourslist(username, project)
            result.append('%s: %s' % (desc, ' '.join(report)))
        l = getcontrib(username)
        for project in l:
            owner = getowner(username, project)
            desc = getdesc(owner, project) or project
            report = gethourslist(owner, project)
            result.append('%s: %s' % (desc, ' '.join(report)))
        if result:
            ievent.reply('', result, dot=True)
        else:
            ievent.reply('no projects found')
    else:
        project = ievent.rest.strip().lower()
        if hasproject(username, project):
            owner = username
        elif hascontrib(username, project):
            owner = getowner(username, project)
        else:
            ievent.reply('no project %s' % project)
            return
        desc = getdesc(owner, project) or project
        report = gethourslist(owner, project)
        ievent.reply('%s: ' % desc, report, dot=True)

cmnds.add('pt-report', handle_report, 'USER')
examples.add('pt-report', 'report hours of work on a project', \
'1) pt-report 2) pt-report gc')

def handle_addshare(bot, ievent):
    """ share a project with another user """
    username = users.getname(ievent.userhost)
    try:
        project, otheruser = ievent.rest.split(' ', 1)
    except ValueError:
        ievent.missing('<projectname> <user>')
        return
    project = project.strip().lower()
    if hascontrib(username, project):
        ievent.reply('only project owner can share a project')
        return
    if not hasproject(username, project):
        ievent.reply('no project %s' % project)
        return
    if not users.exist(otheruser):
        ievent.reply('unknown user %s' % otheruser)
        return
    if hasproject(otheruser, project) or \
    hascontrib(otheruser, project):
        ievent.reply('%s already has a project named %s' \
        % (otheruser, project))
        return
    addshare(username, project, otheruser)
    desc = getdesc(username, project) or project
    ievent.reply('sharing %s with %s' % (desc, otheruser))

cmnds.add('pt-share', handle_addshare, 'USER')
examples.add('pt-share', 'share a project with another user', \
'pt-share myproject knorrie')

def handle_sharelist(bot, ievent):
    """ get a list of users we share a project with """
    username = users.getname(ievent.userhost)
    if not ievent.rest:
        ievent.missing('<projectname>')
        return
    project = ievent.rest.strip().lower()
    if hasproject(username, project):
        l = getsharelist(username, project)
        desc = getdesc(username, project) or project
	if not l:
	    ievent.reply('not sharing %s' % desc)
	else:
            ievent.reply('sharing %s with: ' % desc, l)
    elif hascontrib(username, project):
        owner = getowner(username, project)
        desc = getdesc(owner, project) or project
        l = getsharelist(owner, project)
        ievent.reply('owner is %s, sharing with: '\
        % owner, l)
    else:
        ievent.reply('no project %s' % project)

cmnds.add('pt-sharelist', handle_sharelist, 'USER')
examples.add('pt-sharelist', 'get a list of users we share a project \
with', 'pt-sharelist myproject')

def handle_delshare(bot, ievent):
    """ stop sharing a project with another user """
    username = users.getname(ievent.userhost)
    try:
        project, otheruser = ievent.rest.split(' ', 1)
    except ValueError:
        ievent.missing('<projectname> <user>')
        return
    project = project.strip().lower()
    if not hasproject(username, project):
        ievent.reply('no project %s' % project)
        return
    if not hascontrib(otheruser, project) or \
    getowner(otheruser, project) != username:
        ievent.reply('project not shared with %s' % otheruser)
        return
    delshare(username, project, otheruser)
    desc = getdesc(username, project) or project
    ievent.reply('stopped sharing %s with %s' % (desc, otheruser))

cmnds.add('pt-delshare', handle_delshare, 'USER')
examples.add('pt-delshare', 'stop sharing a project with another \
user', 'pt-delshare myproject somebody')

