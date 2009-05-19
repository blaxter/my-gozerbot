# plugs/shoutcast.py
#
#

""" shoutcast watcher """

__copyright__ = 'this file is in the public domain'

from gozerbot.persist.persist import Persist
from gozerbot.commands import cmnds
from gozerbot.generic import geturl, striphtml, rlog, lockdec
from gozerbot.datadir import datadir
from gozerbot.fleet import fleet
from gozerbot.examples import examples
from gozerbot.threads.thr import start_new_thread
from gozerbot.plughelp import plughelp
from gozerbot.persist.persistconfig import PersistConfig
import os, time, thread

plughelp.add('shoutcast', 'query a shoutcast server or periodically watch \
them')

cfg = PersistConfig()
cfg.define('scwatch', 0)
cfg.define('nodes', [])

sclock = thread.allocate_lock()
locked = lockdec(sclock)

class SCwatcher(object):

    def __init__(self):
        self.stop = False
        self.songsplayed = []

    def run(self):
        self.starttime = int(time.time())
        res = ""
        while cfg.get('scwatch') and not self.stop:
            time.sleep(1)
            if self.stop:
                break
            godo = []    
            for botname, channel, name, node, polltime in cfg.get('nodes'):
                if not (int(time.time()) - self.starttime) % int(polltime):
                    godo.append((botname, channel, name, node))
                    continue            
            if godo:
                rlog(0, 'shoutcast', 'running scan: %s' % str(godo))
                start_new_thread(self.doscan, (godo, ))        

    @locked
    def doscan(self, scanlist):
        for botname, channel, name, node in scanlist:            
            try:
                result = geturl('http://%s/7.html' % node)
            except Exception, ex:
                rlog(10, 'shoutcast', "can't get %s shoutcast data: %s" % \
(node, str(ex)))
                continue
            try:
                res = result.split(',')[6]
            except IndexError:
                rlog(10, 'shoutcast', "can't match %s shoutcast data" % node)
                continue
            song = striphtml(res).strip().replace('\n', '')
            bot = fleet.byname(botname)
            if bot and channel in bot.state['joinedchannels']:
                got = False
                for ttime, played in self.songsplayed:
                    if played == song:
                        got = True
                if not got:
                    self.songsplayed.append((time.time(), song))
                    bot.say(channel, "now playing on %s: %s" % (name, song))
                else:
                    for ttime, played in self.songsplayed:
                        if time.time() - ttime > 1800:
                            self.songsplayed.remove((ttime, played))

scwatcher = SCwatcher()
 
def init():
    if cfg.get('scwatch'):
         start_new_thread(scwatcher.run, ())
    return 1

def shutdown():
    rlog(10, 'shoutcast', 'shutting down watcher')
    scwatcher.stop = True

def handle_sc(bot, ievent):
    try:
        server = ievent.args[0]
    except IndexError:
        ievent.missing('<server>')
        return
    try:
        result = geturl('http://%s/7.html' % server)
    except Exception, ex:
        ievent.reply("can't get shoutcast data: %s" % str(ex))
        return
    try:
        res = result.split(',')[6]
    except IndexError:
        ievent.reply("can't extract shoutcast data")
        return
    ievent.reply(striphtml(res).strip())

cmnds.add('sc', handle_sc, 'USER')
examples.add('sc', 'sc <host:port> .. ask server:port for currently running \
song', 'sc stream1.jungletrain.net:8000')

def handle_sclist(bot, ievent):
    ievent.reply("shoutcast nodes: %s" % cfg.get('nodes'))
    
cmnds.add('sc-list', handle_sclist, 'OPER')
examples.add('sc-list', 'show list of watched shoutcast servers', 'sc-list')

def handle_scadd(bot, ievent):
    try:
        name, node, polltime = ievent.args
    except ValueError:
        ievent.missing('<name> <host:port> <polltime>')
        return
    try:
        polltime = int(polltime)
    except ValueError:
        ievent.reply('polltime needs to be an integer')
        return
    if polltime < 60:
        ievent.reply('polltime in min. 60 seconds')
        return
    if not cfg.get('scwatch'):
        cfg.set('scwatch', 1)
        scwatcher.stop = False    
        start_new_thread(scwatcher.run, ())
    cfg.append('nodes', [bot.name, ievent.channel, name, node, polltime])
    cfg.save()
    ievent.reply('%s added' % node)
    
cmnds.add('sc-add', handle_scadd, 'OPER')
examples.add('sc-add', 'sc-add <server:port> .. add server to watcher', \
'sc-add jungletrain stream1.jungletrain.net 180')

def handle_scdel(bot, ievent):
    try:
        name = ievent.args[0].lower()
    except IndexError:
        ievent.missing('<name>')
        return
    got = 0
    nodes = cfg.get('nodes')
    for i in range(len(nodes)-1, -1, -1):
        if nodes[i][2].lower() == name:
            del nodes[i]
            got = 1
    if got:
        cfg.save()
        ievent.reply('%s deleted' % name)
    else:
        ievent.reply('%s is not in nodeslist' % name)

cmnds.add('sc-del', handle_scdel, 'OPER')
examples.add('sc-del', 'sc-del <name> .. remove node <name> from watcher', \
'sc-del jungletrain')

def handle_scsetpolltime(bot, ievent):
    try:
        name, sec = ievent.args
        sec = int(sec)
    except ValueError:
        ievent.missing('<name> <secondstosleep>')
        return
    if sec < 60:
        ievent.reply('minimun is 60 seconds')
        return
    name = name.lower()
    got = False
    for i in cfg.get('nodes'):
        if i[2].lower() == name:
            i[4] = sec
            got = True
    if got:
        cfg.save()
        ievent.reply('poll time set to %s' % sec)
    else:
        ievent.reply('%s is not in nodes list' % name)
        
cmnds.add('sc-setpolltime', handle_scsetpolltime, 'OPER')
examples.add('sc-setpolltime', 'set poll time of the shoutcast watcher', \
'sc-setpolltime jungletrain 120')

def handle_scpolltime(bot, ievent):
    try:
        name = ievent.args[0].lower()
    except IndexError:
        ievent.missing('<name>')
        return
    for i in cfg.get('nodes'):
        if i[2].lower() == name:
            ievent.reply("polltime of %s is %s" % (name, i[4]))
            return
            
cmnds.add('sc-polltime', handle_scpolltime, 'OPER')
examples.add('sc-polltime', 'get polltime of <name>', 'sc-polltime \
jungletrain')

def handle_scstartwatch(bot, ievent):
    if cfg.get('scwatch'):
        ievent.reply('shoutcast watcher is already running')
        return
    scwatcher.stop = False
    cfg.set('scwatch', 1)
    start_new_thread(scwatcher.run, ())
    ievent.reply('watcher started')
    
cmnds.add('sc-startwatch', handle_scstartwatch, 'OPER')
examples.add('sc-startwatch', 'start the shoutcast watcher', 'sc-startwatch')

def handle_scstopwatch(bot, ievent):
    scwatcher.stop = True
    cfg.set('scwatch', 0)
    ievent.reply('watcher stopped')
    
cmnds.add('sc-stopwatch', handle_scstopwatch, 'OPER')
examples.add('sc-stopwatch', 'stop the shoutcast watcher', 'sc-stopwatch')
