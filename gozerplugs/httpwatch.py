import md5
import os

from gozerbot.commands import cmnds
from gozerbot.datadir import datadir
from gozerbot.fleet import fleet
from gozerbot.generic import geturl2
from gozerbot.periodical import periodical
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.persist.pdod import Pdod
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
import gozerbot.threads.thr as thr

plughelp.add('httpwatch', 'periodically check urls')

cfg = PersistConfig()
cfg.define('sleep', 300)
cfg.define('run', True)

class HttpWatch(Pdod):
    
    pid = None

    def __init__(self):
        self.datadir = datadir + os.sep + 'plugs' + os.sep + 'httpwatch'
        Pdod.__init__(self, os.path.join(self.datadir, 'httpwatch.data'))
        if not 'urls' in self.data:
            self.data['urls'] = {}
        if not 'send' in self.data:
            self.data['send'] = {}
            self.save()

    def start(self):
        self.pid = periodical.addjob(cfg.get('sleep'), 0, self.peek, 'httpwatch', 'httpwatch')
 
    def stop(self):
        if self.pid:
            periodical.killjob(self.pid)
            self.pid = None

    def peek(self, *args, **kwargs):
        if not self.data['urls']: return
        for url in self.data['urls']:
            try:
                checksum = self.checksum(url)
            except:
                continue
            
            if checksum != self.data['urls'][url]:
                self.data['urls'][url] = checksum
                self.announce(url)
        self.save()
        return self.data['urls']

    def checksum(self, url):
        data = geturl2(url)
        return md5.new(data).hexdigest()

    def announce(self, url):
        for name in self.data['send'][url]:
            bot = fleet.byname(name)
            for chan in self.data['send'][url][name]:
                bot.say(chan, '%s changed (new checksum: %s)' % (url, \
self.data['urls'][url]))

    def add(self, url, name, chan):
        if not url in self.data['urls']:
            self.data['urls'][url] = ''
        if not url in self.data['send']:
            self.data['send'][url] = {}
        if not name in self.data['send'][url]:
            self.data['send'][url][name] = []
        if not chan in self.data['send'][url][name]:
            self.data['send'][url][name].append(chan)
            self.save()

    def remove(self, url, name, chan):
        if url not in self.data['send']:
            return
        if name not in self.data['send'][url]:
            return
        if chan in self.data['send'][url][name]:
            self.data['send'][url][name].remove(chan)
        if len(self.data['send'][url][name]) == 0:
            del self.data['send'][url][name]
        if len(self.data['send'][url]) == 0:
            del self.data['send'][url]
        self.save()

httpwatch = HttpWatch()

def init():
    if cfg.get('run'):
        thr.start_new_thread(httpwatch.start, ())
    return 1

def shutdown():
    if httpwatch.pid:
        httpwatch.stop()
    return 1

def handle_httpwatch_add(bot, ievent):
    if len(ievent.args) != 1:
        ievent.missing('<url>')
    else:
        try:
            geturl2(ievent.args[0])
            httpwatch.add(ievent.args[0], bot.name, ievent.channel)
            ievent.reply('http watcher added')
        except Exception, e:
            ievent.reply('failed to add: %s' % (str(e),))

def handle_httpwatch_del(bot, ievent):
    if len(ievent.args) != 1:
        ievent.missing('<url>')
    else:
        httpwatch.remove(ievent.args[0], bot.name, ievent.channel)
        ievent.reply('http watcher removed')

def handle_httpwatch_list(bot, ievent):
    ievent.reply(str(httpwatch.data['send']))

def handle_httpwatch_peek(bot, ievent):
    ievent.reply('running httpwatch.peek()')
    ievent.reply(str(httpwatch.peek()))

def handle_httpwatch_start(bot, ievent):
    if httpwatch.pid:
        ievent.reply('watcher already running (pid: %s)' % (str(httpwatch.pid),))
    else:
        httpwatch.start()
        ievent.reply('watcher started')

def handle_httpwatch_stop(bot, ievent):
    if httpwatch.pid:
        httpwatch.stop()
        ievent.reply('watcher stopped')
    else:
        ievent.reply('watcher not running')

cmnds.add('httpwatch-add', handle_httpwatch_add, 'OPER')
cmnds.add('httpwatch-del', handle_httpwatch_del, 'OPER')
cmnds.add('httpwatch-list', handle_httpwatch_list, 'OPER')
cmnds.add('httpwatch-peek', handle_httpwatch_peek, 'OPER')
cmnds.add('httpwatch-start', handle_httpwatch_start, 'OPER')
cmnds.add('httpwatch-stop', handle_httpwatch_stop, 'OPER')

