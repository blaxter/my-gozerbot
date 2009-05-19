# -*- coding: utf-8 -*-
# Support for bugtrackers
# Wijnand 'tehmaze' Modderman - http://tehmaze.com
# BSD License
#
# ======
#  TODO
# ======
#  * add authorization support to bugtrackers
#  * add write support to bugtrackers (close/open bug)
#
# ======
#  BUGS 
# ======
#  * I did test these bugtrackers on various installations, although not everything
#    will work on all installations, for example on older versions or on bugtrackers
#    that restyled the complete layout

from gozerbot.aliases import aliases
from gozerbot.callbacks import callbacks
from gozerbot.commands import cmnds
from gozerbot.datadir import datadir
from gozerbot.examples import examples
from gozerbot.generic import geturl, geturl2, striphtml, useragent
from gozerbot.persist.pdod import Pdod
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.plughelp import plughelp
from gozerbot.users import users
from gozerbot.utils.generic import convertpickle
import copy
import os
import re
import urllib, urllib2
import xml.dom.minidom

plughelp.add('bugtracker', 'various bug tracker support, define a bugtracker for the channel with bugtracker-set')

cfg = PersistConfig()
cfg.define('sep', '..')

class BugTrackerNotFound(Exception):
    pass

class BugTrackerNotImplemented(Exception):
    pass

class BugTrackerNotSupported(Exception):
    pass

class BugTracker:

    bugurls = [] # regexp patterns that could match a bugtracker url
    bugtags = re.compile('(?:bug|ticket)\s?#(\d+)', re.I)

    def __init__(self, baseUrl, autoshow):
        self.url = baseUrl.rstrip('/')
        self.autoshow = autoshow

    def close(self, bugId, userhost='', message='', action=''):
        raise BugTrackerNotImplemented

    def close_url(self, bugId):
        raise BugTrackerNotImplemented

    def comments(self, bugId):
        raise BugTrackerNotImplemented

    def comments_url(self, bugId):
        raise BugTrackerNotImplemented

    def list(self):
        raise BugTrackerNotImplemented

    def list_url(self):
        raise BugTrackerNotImplemented

    def open(self, message=''):
        raise BugTrackerNotImplemented

    def open_url(self):
        raise BugTrackerNotImplemented

    def show(self, bugId):
        raise BugTrackerNotImplemented

    def show_url(self, bugId):
        raise BugTrackerNotImplemented
        
    def handle_close(self, bot, ievent):
        if len(ievent.args) < 3:
            ievent.missing('<bug id> <action> <message>')
            return
        try:
            status = self.close(ievent.args[0], users.getname(ievent.userhost), 
                ' '.join(ievent.args[2:]), ievent.args[1])
            ievent.reply('ok')
        except AssertionError, e:
            ievent.reply('error: %s' % e)
        except BugTrackerNotImplemented:
            ievent.reply('error: not implemented in this bug tracker')
        except BugTrackerNotSupported, e:
            ievent.reply('error: not supported: %s' % e)
        except BugTrackerNotFound, e:
            ievent.reply('error: not found: %s' % e)

    def handle_comments(self, bot, ievent):
        if not ievent.args or not ievent.args[0].isdigit():
            ievent.missing('<bug id>')
            return
        try:
            comments = self.comments(ievent.args[0])
            if comments:
                ievent.reply('comments: ', comments, dot=' %s ' % cfg.get('sep'), nr=True, nritems=True)
            else:
                ievent.reply('no comments found')
        except AssertionError, e:
            ievent.reply('error: %s' % e)
        except BugTrackerNotImplemented:
            ievent.reply('error: not implemented in this bug tracker')
        except BugTrackerNotSupported, e:
            ievent.reply('error: not supported: %s' % e)
        except BugTrackerNotFound, e:
            ievent.reply('error: not found: %s' % e)

    def handle_list(self, bot, ievent):
        try:
            bugs = self.list()
            if bugs:
                ievent.reply('open bugs: ', bugs, dot=' %s ' % cfg.get('sep'))
            else:
                ievent.reply('no open bugs found!')
        except BugTrackerNotImplemented:
            ievent.reply('error: not implemented in this bug tracker')
        except BugTrackerNotSupported, e:
            ievent.reply('error: not supported: %s' % e)
        except BugTrackerNotFound, e:
            ievent.reply('error: not found: %s' % e)

    def handle_show(self, bot, ievent):
        if len(ievent.args) != 1:
            try:
                open_url = self.open_url()
                ievent.missing('<bug id> -- if you were looking to report a bug, please go to %s' % open_url)
            except BugTrackerNotImplemented:
                ievent.missing('<bug id>')
            return
        try:
            status = self.show(ievent.args[0])
            result = []
            keys   = status.keys() ; keys.sort()
            for key in keys:
                if status[key]:
                    result.append('%s=%s' % (key, status[key]))
            result.append(self.show_url(ievent.args[0]))
            ievent.reply(result, dot=' %s ' % cfg.get('sep'))
        except AssertionError, e:
            ievent.reply('error: %s' % e)
        except BugTrackerNotImplemented:
            ievent.reply('error: not implemented in this bug tracker')
        except BugTrackerNotSupported, e:
            ievent.reply('error: not supported: %s' % e)
        except BugTrackerNotFound, e:
            ievent.reply('error: not found: %s' % e)

    def scan_privmsg(self, bot, ievent):
        if not self.autoshow:
            return
        if not self.bugurls:
            return
        for bugurl in self.bugurls:
            test = bugurl.findall(ievent.origtxt)
            if test:
                nevent = copy.copy(ievent)
                nevent.args = [test[0]]
                self.handle_show(bot, nevent)
                del nevent
                return
        test = self.bugtags.findall(ievent.origtxt)
        if test:
            nevent = copy.copy(ievent)
            nevent.args = [test[0]]
            self.handle_show(bot, nevent)
            del nevent
            return

class Bugzilla(BugTracker):
    def __init__(self, url, autoshow):
        BugTracker.__init__(self, url, autoshow)
        self.bugurls = [
            re.compile(r'%s/show_bug.*id=(\d+)' % self.url)
            ]

    def list(self):
        csv = geturl2(self.list_url_summary())
        num = 0
        for line in csv.splitlines():
            try:
                num += int(line.split(',')[1])
            except ValueError:
                pass
        bugs = []
        if num > 100:
            bugs.append('showing 100-%d' % num)
        csv = geturl2(self.list_url())
        for line in csv.splitlines()[1:]:
            part = line.split(',')
            bugs.append('%s (%s)' % (part[0], part[1].replace('"', '')))
            if len(bugs) > 100:
                break
        return bugs        

    def list_url(self):
        return '%s/buglist.cgi?=&action=wrap&bug_file_loc=&bug_file_loc_type=allwordssubstr&bug_id=&bug_status=NEW&bug_status=ASSIGNED&bug_status=REOPENED&bugidtype=include&chfieldfrom=&chfieldto=Now&chfieldvalue=&email1=&email2=&emailtype1=substring&emailtype2=substring&field-1-0-0=bug_status&field0-0-0=noop&keywords=&keywords_type=allwords&long_desc=&long_desc_type=substring&query_format=advanced&remaction=&short_desc=&short_desc_type=allwordssubstr&status_whiteboard=&status_whiteboard_type=allwordssubstr&type-1-0-0=anyexact&type0-0-0=noop&value-1-0-0=NEW%%2CASSIGNED%%2CREOPENED&value0-0-0=&ctype=csv' % self.url

    def list_url_summary(self):
        return '%s/report.cgi?bug_file_loc=&bug_file_loc_type=allwordssubstr&bug_id=&bug_status=NEW&bug_status=ASSIGNED&bug_status=REOPENED&bugidtype=include&chfieldfrom=&chfieldto=Now&chfieldvalue=&email1=&email2=&emailtype1=substring&emailtype2=substring&field0-0-0=noop&keywords=&keywords_type=allwords&long_desc=&long_desc_type=substring&short_desc=&short_desc_type=allwordssubstr&status_whiteboard=&status_whiteboard_type=allwordssubstr&type0-0-0=noop&value0-0-0=&x_axis_field=&y_axis_field=bug_status&z_axis_field=&width=600&height=350&action=wrap&ctype=csv&format=table' % self.url

    def show(self, bugId):
        assert bugId.isdigit(), "bug id has to be a number"
        bugxml = geturl(self.show_url_xml(bugId))
        bugdom = xml.dom.minidom.parseString(bugxml)
        try:
            bugset = bugdom.getElementsByTagName('bug')[0]
        except:
            raise BugTrackerNotFound('could not find bug tag')
        bugget = {'creation_ts': 'created', 'product': 'product', 'component': 'component',
            'version': 'version', 'bug_status': 'status', 'resolution': 'resolution',
            'priority': 'priority', 'bug_severity': 'severity', 'reporter': 'reporter',
            'short_desc': 'description', 'assigned_to': 'assigned to'}
        data = {}
        for tag in bugget.keys():
            try:
                value = bugset.getElementsByTagName(tag)[0].firstChild.nodeValue
                data[bugget[tag]] = value
            except:
                pass
        return data

    def show_url(self, bugId):
        assert bugId.isdigit(), "bug id has to be a number"
        return '%s/show_bug.cgi?id=%s' % (self.url, bugId)

    def show_url_xml(self, bugId):
        assert bugId.isdigit(), "bug id has to be a number"
        return '%s/show_bug.cgi?ctype=xml&id=%s' % (self.url, bugId)

class Flyspray(BugTracker):
    def __init__(self, url, autoshow):
        BugTracker.__init__(self, url, autoshow)
        self.bugurls = [
            re.compile(r'%s/task/(\d+)' % self.url)
            ]

    def list(self):
        bugrss = geturl(self.list_url())
        bugdom = xml.dom.minidom.parseString(bugrss)
        bugall = bugdom.getElementsByTagName('entry')
        bugs = []
        if bugall:
            for entry in bugall:
                try:
                    bugid = entry.getElementsByTagName('id')[0].firstChild.nodeValue.split(':')[2]
                    bugs.append(bugid)
                except:
                    pass
        return bugs

    def list_url(self):
        return '%s/feed.php?feed_type=atom&project=' % self.url

    def show(self, bugId):
        assert bugId.isdigit(), "bug id has to be a number"
        html = geturl2(self.show_url(bugId))
        data = {}
        stat = ''
        for line in html.splitlines():
            line = line.strip()
            if not line:
                continue
            elif '<td headers="category">' in line:
                stat = 'category'
            elif '<td headers="status">' in line:
                stat = 'status'
            elif '<td headers="assignedto">' in line:
                stat = 'assigned to'
            elif '<td headers="os">' in line:
                data['os'] = striphtml(line).strip()
            elif '<td headers="severity">' in line:
                data['severity'] = striphtml(line).strip()
            elif '<td headers="priority">' in line:
                data['priority'] = striphtml(line).strip()
            elif '<td headers="reportedver">' in line:
                data['version'] = striphtml(line).strip()
            elif '<h2 class="summary' in line:
                stat = 'summary'
            elif '<a href="#comments">Comments (' in line:
                data['comments'] = line.split('(', 1)[1].split(')')[0]
            # stats
            elif stat:
                if stat in ['category', 'status', 'assigned to', 'summary']:
                    data[stat] = striphtml(line).strip()
                stat = ''
        return data

    def show_url(self, bugId):
        assert bugId.isdigit(), "bug id has to be a number"
        return '%s/task/%s' % (self.url, bugId)

class GoogleCode(BugTracker):
    def __init__(self, url, autoshow):
        BugTracker.__init__(self, url, autoshow)
        self.bugurls = [
            re.compile(r'%s/issues.*id=(\d+)' % self.url)
            ]

    def close(self, *args):
        raise BugTrackerNotSupported("google code needs authorization which I don't support")

    def list(self):
        html = geturl2(self.list_url())
        bugs = []
        for line in html.splitlines():
            if '<a href="detail?id' in line and '&amp;' in line:
                bug = line.split('id=')[1].split('&amp;')[0]
                if not bug in bugs:
                    bugs.append(bug)
        return bugs

    def list_url(self):
        return '%s/issues/list' % self.url

    def open(self, *args):
        raise BugTrackerNotSupported("google code needs authorization which I don't support")

    def show(self, bugId):
        assert bugId.isdigit(), "bug id has to ba a number"
        html = geturl2(self.show_url(bugId)).splitlines()
        data = {}
        stat = ''
        for line in html:
            line = line.strip()
            if not line:
                continue
            if line.startswith('<span class=h3 >'):
                data['summary'] = striphtml(line)
            elif line.startswith('<tr><th align=left>Status:'):
                stat = 'status'
            elif line.startswith('class=label><b>Type-</b>'):
                data['type'] = striphtml(line.split('</b>')[1])
            elif line.startswith('class=label><b>Priority-</b>'):
                data['priority'] = striphtml(line.split('</b>')[1])
            elif line.startswith('<span class=author>') and not data.has_key('author'):
                stat = 'author'
            elif line.startswith('<tr><th align=left>Owner:'):
                stat = 'owner'
            elif line.startswith('<span class="date" title="'):
                data['date'] = striphtml(line)
            elif striphtml(line) == '':
                pass
            # stats
            elif stat == 'author':
                data['reporter'] = striphtml(line)
                stat = ''
            elif stat == 'owner':
                data['owner'] = striphtml(line)
                stat = ''
            elif stat == 'status':
                data['status'] = striphtml(line)
                stat = ''
        return data

    def show_url(self, bugId):
        assert bugId.isdigit(), "bug id has to be a number"
        return '%s/issues/detail?id=%s' % (self.url.rstrip('/'), bugId)

class Mantis(BugTracker):
    def __init__(self, url, autoshow):
        BugTracker.__init__(self, url, autoshow)

    def show(self, bugId):
        assert bugId.isdigit(), "bug id has to be a number"
        html = geturl2(self.show_url(bugId))
        if 'APPLICATION ERROR #1100' in html:
            raise BugTrackerNotFound('issue not found')
        data = {'notes': 0}
        stat = ''
        skip = 0
        for line in html.splitlines():
            line = line.strip().replace('\t', '')
            if skip > 0:
                skip -= 1
                continue
            elif not line:
                continue
            elif '<!-- Category -->' in line:
                skip = 1
                stat = 'category'
            elif '<!-- Severity -->' in line:
                skip = 1
                stat = 'severity'
            elif '<!-- Reproducibility -->' in line:
                skip = 1
                stat = 'reproducibility'
            elif '<!-- Reporter -->' in line:
                skip = 3
                stat = 'reporter'
            elif '<!-- Priority -->' in line:
                skip = 1
                stat = 'priority'
            elif '<!-- Resolution -->' in line:
                skip = 1
                stat = 'resolution'
            elif '<!-- Status -->' in line:
                skip = 3
                stat = 'status'
            elif '<!-- Summary -->' in line:
                skip = 4
                stat = 'summary'
            elif '<td class="bugnote-public">' in line:
                data['notes'] += 1
            # stats
            elif stat:
                if stat in ['category', 'severity', 'reproducibility', 'reporter',
                    'priority', 'resolution', 'status', 'summary']:
                    data[stat] = striphtml(line)
                stat = ''
        return data

    def show_url(self, bugId):
        assert bugId.isdigit(), "bug id has to be a number"
        return '%s/view.php?id=%s' % (self.url.rstrip('/'), bugId)

class Trac(BugTracker):
    def __init__(self, url, autoshow):
        BugTracker.__init__(self, url, autoshow)
        self.bugurls = [
            re.compile(r'%s/ticket/(\d+)' % self.url)
            ]

    def comments(self, bugId):
        assert bugId.isdigit(), "bug id has to be a number"
        bugrss = geturl(self.comments_url(bugId))
        bugdom = xml.dom.minidom.parseString(bugrss)
        bugall = bugdom.getElementsByTagName('item')
        comments = []
        if bugall:
            for item in bugall:
                title = item.getElementsByTagName('title')[0].firstChild.nodeValue
                if 'comment added' in title:
                    try:
                        author = item.getElementsByTagName('dc:creator')[0].firstChild.nodeValue
                    except IndexError:
                        author = 'anonymous'
                    comment = item.getElementsByTagName('description')[0].firstChild.nodeValue
                    comment = striphtml(comment.replace('\n', ' ')).strip()
                    while '  ' in comment:
                        comment = comment.replace('  ', ' ')
                    comments.append('%s: %s' % (author, comment))
        return comments    

    def comments_url(self, bugId):
        assert bugId.isdigit(), "bug id has to be a number"
        return '%s/ticket/%s?format=rss' % (self.url, bugId)

    def list(self):
        tsv = geturl2(self.list_url()).splitlines()
        bugs = []
	keys = map(lambda x: x.strip(), tsv[0].split())
	for item in tsv[1:]:
		data = {}
		part = item.split('\t')
		# dirty hack to allow unescaped multilines in trac
		if part[0].isdigit() and part[1].isdigit() and len(part) == len(keys):
			data = dict(zip(keys, part))
			bugs.append('%s (%s)' % (data['summary'], data['ticket']))
        return bugs

    def list_url(self):
        return '%s/report/1?format=tab&USER=anonymous' % self.url

    def show(self, bugId):
        assert bugId.isdigit(), "bug id has to be a number"
        tsv = geturl2(self.show_url(bugId)+'?format=tab').splitlines()
	keys = map(lambda x: x.strip(), tsv[0].split())
	part = tsv[1].split('\t')
	data = dict(zip(keys, part))
        return data

    def show_url(self, bugId):
        assert bugId.isdigit(), "bug id has to be a number"
        return '%s/ticket/%s' % (self.url, bugId)

    def open(self, reporter, message, type='defect', priority='minor'):
        postdata = {
            'reporter':        reporter,
            'summary':         message,
            'type':            type,
            'description':     message,
            'priority':        priority,
            'milestone':       '',
            'component':       '',
            'version':         '',
            'keywords':        '',
            'owner':           '',
            'cc':              '',
            # hidden stuff
            'action':          'create',
            'status':          'new',
            }

    def open_url(self):
        return '%s/newticket' % self.url

    def close(self, bugId, reporter, message, action='fixed'):
        actions = ['fixed', 'invalid', 'wontfix', 'duplicate', 'worksforme']
        # input check
        assert bugId.isdigit(), "bug id has to be a number"
        assert action in actions, "action has to be one of: %s" % ', '.join(actions)
        showdata = self.show(bugId) 
        postdata = {
            'reporter':         reporter,
            'comment':          message,
            'action':           'resolve',
            'type':             'defect',
            'resolve_resolution': action,
            'summary':          showdata['summary'],
            'priority':         showdata['priority'],
            'milestone':        showdata['milestone'],
            'component':        showdata['component'],
            'version':          showdata['version'],
            'keywords':         showdata['keywords'],
            'cc':               '',
            }
        postdata = urllib.urlencode(postdata)
        req = urllib2.Request('%s/ticket/%s' % (self.url, bugId), data=postdata)
        req.add_header('User-agent', useragent())
        return urllib2.urlopen(req).read()

class BugManager(Pdod):

    types = {
        'bugzilla': Bugzilla,
        'flyspray': Flyspray,
        'googlecode': GoogleCode,
        'mantis': Mantis,
        'trac': Trac
        }
    instances = {
        }

    def __init__(self):
        Pdod.__init__(self, os.path.join(datadir + os.sep + 'plugs' + os.sep \
+ 'bugtracker', 'bugtracker'))
        self.load()

    def add(self, bot, ievent, type, url):
        assert type in self.types.keys(), "unknown bugtracker type, supported: %s" % ', '.join(self.types.keys())
        if hasattr(bot, 'name'):
            botname = bot.name
        else:
            botname = bot
        if hasattr(ievent, 'channel'):
            channel = ievent.channel
        else:
            channel = ievent
        if not self.data.has_key(botname):
            self.data[botname] = {}
        self.data[bot.name][channel] = [url, type, False]
        self.save()
        self.start(bot, ievent)

    def check(self, bot, ievent):
        if not self.instances.has_key(bot.name):
            return False
        if not self.instances[bot.name].has_key(ievent.channel):
            return False
        return True

    def load(self):
        for bot in self.data.keys():
            for channel in self.data[bot].keys():
                self.start(bot, channel)
                
    def start(self, bot, ievent):
        if hasattr(bot, 'name'):
            botname = bot.name
        else:
            botname = bot
        if hasattr(ievent, 'channel'):
            channel = ievent.channel
        else:
            channel = ievent
        if not self.instances.has_key(botname):
            self.instances[botname] = {}
        data = self.data[botname][channel]
        if not len(data) == 3:
            data.append(False)
            self.data[botname][channel] = data
            self.save()
        self.instances[botname][channel] = self.types[data[1]](data[0], data[2])

    # "internals"
    def handle_tracker_info(self, bot, ievent):
        if not self.check(bot, ievent):
            ievent.reply('no bugtracker active on %s' % ievent.channel)
        else:
            data = self.data[bot.name][ievent.channel]
            ievent.reply('bugtracker type: %s .. url: %s .. autoshow: %s' % (data[1], data[0], str(data[2])))
    
    def handle_tracker_set(self, bot, ievent):
        if len(ievent.args) != 2:
            ievent.missing('<type> <url>')
            return
        try:
            self.add(bot, ievent, ievent.args[0], ievent.args[1])
            ievent.reply('ok')
        except AssertionError, e:
            ievent.reply('error: %s' % e) 

    def handle_autoshow(self, bot, ievent):
        if not self.check(bot, ievent):
            ievent.reply('no bugtracker configured')
            return
        self.data[bot.name][ievent.channel][2] = not self.data[bot.name][ievent.channel][2]
        try:
            self.instances[bot.name][ievent.channel].autoshow = self.data[bot.name][ievent.channel][2]
        except:
            pass
        self.save()
        ievent.reply('autoshow is now %s' % str(self.data[bot.name][ievent.channel][2]))

    # proxies
    def handle_close(self, bot, ievent):
        if not self.check(bot, ievent):
            ievent.reply('no bugtracker configured')
            return
        try:
            self.instances[bot.name][ievent.channel].handle_close(bot, ievent)
        except Exception, e:
            ievent.reply('failed to get bug information: %s' % str(e))

    def handle_comments(self, bot, ievent):
        if not self.check(bot, ievent):
            ievent.reply('no bugtracker configured')
            return
        #try:
	self.instances[bot.name][ievent.channel].handle_comments(bot, ievent)
        #except Exception, e:
        #    ievent.reply('failed to get bug information: %s' % str(e))
    
    def handle_list(self, bot, ievent):
        if not self.check(bot, ievent):
            ievent.reply('no bugtracker configured')
            return
        self.instances[bot.name][ievent.channel].handle_list(bot, ievent)
        return
        try:
            self.instances[bot.name][ievent.channel].handle_list(bot, ievent)
        except Exception, e:
            ievent.reply('failed to get bug information: %s' % str(e))

    def handle_open(self, bot, ievent):
        if not self.check(bot, ievent):
            ievent.reply('no bugtracker configured')
            return
        try:
            self.instances[bot.name][ievent.channel].handle_open(bot, ievent)
        except Exception, e:
            ievent.reply('failed to get bug information: %s' % str(e))

    def handle_show(self, bot, ievent):
        if not self.data.has_key(bot.name):
            ievent.reply('no bugtracker configured')
            return False
        try:
            self.instances[bot.name][ievent.channel].handle_show(bot, ievent)
        except Exception, e:
            ievent.reply('failed to fetch bug information: %s' % str(e))

    def cb_privmsg(self, bot, ievent):
        if not self.instances.has_key(bot.name):
            return 0
        if not self.instances[bot.name].has_key(ievent.channel):
            return 0
        self.instances[bot.name][ievent.channel].scan_privmsg(bot, ievent)

bugtrackers = BugManager()

def init():
    callbacks.add('PRIVMSG', bugtrackers.cb_privmsg)

def upgrade():
    convertpickle(datadir + os.sep + 'old' + os.sep + 'bugtracker', \
datadir + os.sep + 'plugs' + os.sep + 'bugtracker' + os.sep + 'bugtracker')

cmnds.add('bug-autoshow', bugtrackers.handle_autoshow, ['OPER'])
examples.add('bug-autoshow', 'toggle automatic retrieval of bug information', 'bug-autoshow')
cmnds.add('bug-close', bugtrackers.handle_close, ['OPER', 'BUGS'])
examples.add('bug-close', 'close a bug', 'bug-close 42 fixed Typo on line 23')
cmnds.add('bug-comments', bugtrackers.handle_comments, ['USER'])
examples.add('bug-comments', 'show all comments on a bug', 'bug-comments 42')
cmnds.add('bug-list', bugtrackers.handle_list, ['USER', 'BUGS'])
examples.add('bug-list', 'list all open bugs', 'bug-list')
cmnds.add('bug-show', bugtrackers.handle_show, ['USER'])
examples.add('bug-show', 'show a bug', 'bug-show 42')
cmnds.add('bugtracker-info', bugtrackers.handle_tracker_info, ['BUGSOPER', 'OPER'])
cmnds.add('bugtracker-set', bugtrackers.handle_tracker_set, ['BUGSOPER', 'OPER'])
examples.add('bugtracker-set', 'set a bugtracker for the channel', 'bugtracker-set googlcode http://code.google.com/p/gozerbot')
aliases.data['bug'] = 'bug-show'
 
