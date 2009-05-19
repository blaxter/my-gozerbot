#! /usr/bin/env python
#
# Quick'n'dirty doc generator
#
# TODO:
#  * look for author in the hg heads
#  * map user<>full name in this file
#  * use gozerbot to actually process the output of the commands, if able
#

from gozerbot.generic import handle_exception, enable_logging, toascii, \
splittxt, strippedtxt
from gozerbot.plugins import plugins
from gozerbot.irc.ircevent import Ircevent
from gozerbot.examples import examples
from gozerbot.irc.bot import Bot
from gozerbot.users import users
from gozerbot.plughelp import plughelp
from gozerbot.commands import cmnds
from gozerbot.aliases import aliasreverse
from gozerbot.config import config, Config
from gozerbot.fleet import fleet
from gozerbot.redispatcher import rebefore, reafter
from gozerbot.database.alchemy import startmaindb
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
import time
donot = ['quit', 'reboot', 'jump']
config.load()
oldlevel = config['loglevel']
config['loglevel'] = 1000
enable_logging()
startmaindb()
cfg = Config()
bot = Bot(cfg)
bot.channels.setdefault('#test', {})
bot.channels.setdefault('#dunkbots', {})
bot.userhosts['dunker'] = 'bart@gozerbot.org'
bot.userhosts['test'] = 'test@test'
bot.server = 'localhost'
bot.port = 6667
fleet.addbot(bot)
plugins.regplugins()
time.sleep(5)

try:
    users.add('test', ['test@test', ], ['OPER', 'USER', 'QUOTE', 'MAIL'])
except Exception, ex:
    pass

try:
    users.setemail('test', 'bthate@gmail.com')
except Exception, ex:
    pass

def gendoc(f):
    base = os.path.basename(f).replace('.py', '')
    print '=' * (len(base)+2)
    print ' %s ' % base.upper()
    print '=' * (len(base)+2)
    print "| \n"
    print "about"
    print "-----"
    print "| \n"
    try:
        author = plugins.plugs[base].__author__
        print ":author:  %s" % author.strip()
    except AttributeError:
        print ":author:  Bart Thate <bthate@gmail.com>"
    print ":contact: IRCNET/#dunkbots"
    if 'gozerplugs' in f:
        print ':distribution: core'
    else:
        print ":distribution: http://plugins.gozerbot.org"
    try:
        license = plugins.plugs[base].__license__
        print ":license:  %s" % license.strip()
    except AttributeError:
        print ":license: Public Domain"
    print " "
    print "| \n"
    data = {'author': 'unknown', 'description': '', 'commands':[], 'examples':{}, \
'descriptions':{}, 'callbacks': {}, 'aliases': {}, 'permissions': {}}
    data['description'] = plughelp[base]
    cmndlist = []
    for j, z in cmnds.iteritems():
        if j in donot:
            continue
        if z.plugname == base:
            cmndlist.append(j)
    relist = []
    for reitem in rebefore.relist:
        if reitem.plugname == base:
            relist.append(reitem)
    for reitem in reafter.relist:
        if reitem.plugname == base:
            relist.append(reitem)
    cmndlist.sort()
    try:
        first = plugins.plugs[base].__gendocfirst__
        for i in first[::-1]: 
            try:
                cmndlist.remove(i)
            except ValueError:
                continue
            cmndlist.insert(0,i)
    except AttributeError:
        pass
    try:
        first = plugins.plugs[base].__gendoclast__
        for i in first[::-1]: 
            try:
                cmndlist.remove(i)
            except ValueError:
                continue
            cmndlist.append(i)
    except AttributeError:
        pass
    try:
        skip = plugins.plugs[base].__gendocskip__
        for i in skip[::-1]: 
            try:
                cmndlist.remove(i)
            except ValueError:
                continue
    except AttributeError:
        pass
    for command in cmndlist:
        data['commands'].append(command)
        alias = aliasreverse(command)
        if alias:
            data['aliases'][command] = alias
        try:
            ex = examples[command]
        except Exception, exx:
            continue
        try:
            data['permissions'][command] = cmnds.perms(command)
        except: 
            pass
        data['examples'][command] = []
        exampleslist = re.split('\d\)', ex.example)
        for e in exampleslist:
            data['examples'][command].append(e.strip())
            data['descriptions'][command] = ex.descr
    print "description"
    print "-----------"
    print "| \n"
    print data['description'] + '\n'
    try:
        doc = plugins.plugs[base].__doc__
        print "| \n"
        doclist = doc.split('\n')
        for line in doclist:
            print " %s" % line
    except AttributeError:
        pass
    print "\n| \n"
    print 'commands'
    print "--------"
    print "| \n"
    teller = 1
    for command in data['commands']:
        if data['aliases'].has_key(command):
            print '%s) *%s (%s)*' % (teller, command, data['aliases'][command])
        else:
            print '%s) *%s*' % (teller, command)
        if data['descriptions'].has_key(command):
            print '\n    :description: %s' % data['descriptions'][command]
        if data['permissions'].has_key(command):
            print '\n    :permissions: %s' % ' .. '.join(data['permissions']\
[command])
        if data['examples'].has_key(command):
            print '\n    :examples:'
            for i in data['examples'][command]:
                if not i:
                     continue
                print '\n    ::\n\n        <user> !%s' % i.strip()
                output = None
                try:
                    config['loglevel'] = 1000
                    output = bot.test(i.strip(), 16)
                    if not output:
                        print "        <output> none"
                        continue
                    result = ' .. '.join(output)
                    result = result.replace('\002', '')
                    teller2 = 1
                    for j in splittxt(result, 50):
                        if teller2 > 10:
                            print '         - output trunked -'
                            break
                        print '        <output> %s' % j
                        teller2 += 1
                    print '\n'
                except Exception, ex:
                    handle_exception(short=True)
        teller += 1
    if not data['commands']:
        print "no commands in this plugin"
    if relist:
        print "\nregular expressions"
        print "-------------------"
        print "| \n"
        teller = 1
        for reitem in relist:
            print "%s) %s" % (teller, reitem.regex)
            try:
                print "     " + reitem.func.__doc__
            except AttributeError:
                pass
            teller += 1
#config['loglevel'] = oldlevel

if __name__ == '__main__':
    if len(sys.argv) != 2 or not os.path.isfile(sys.argv[1]):
        print '%s <file>' % sys.argv[0]
        sys.exit(1)
    gendoc(sys.argv[1])
    sys.stdout.flush()
