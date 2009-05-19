# interact with (your) Music Player Daemon
# (c) Wijnand 'tehmaze' Modderman - http://tehmaze.com
# BSD License
#
# CHANGELOG
#
#  2008-10-30
#   * fixed "Now playing" when having a password on MPD
#  2007-11-16
#   * added watcher support
#   * added formatting options ('song-status')
#   * added more precision to duration calculation
#  2007-11-10
#   * initial version
#
# REFERENCES
#
#  The MPD wiki is a great resource for MPD information, especially:
#   * http://mpd.wikia.com/wiki/MusicPlayerDaemonCommands
#

__version__ = '2007111601'

import os, socket, time

from gozerbot.utils.generic import convertpickle
from gozerbot.aliases import aliases
from gozerbot.commands import cmnds
from gozerbot.datadir import datadir
from gozerbot.examples import examples
from gozerbot.fleet import fleet
from gozerbot.generic import rlog
from gozerbot.persist.pdod import Pdod
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.plughelp import plughelp
from gozerbot.threads.thr import start_new_thread

plughelp.add('mpd', 'music player daemon control')

## UPGRADE PART

def upgrade():
    convertpickle(datadir + os.sep + 'old' + os.sep + 'mpd', \
datadir + os.sep + 'plugs' + os.sep + 'mpd' + os.sep + 'mpd')


cfg = PersistConfig()
cfg.define('server-host', '127.0.0.1')
cfg.define('server-port', 6600)
cfg.define('server-pass', '')
cfg.define('socket-timeout', 15)
cfg.define('watcher-interval', 10)
cfg.define('watcher-enabled', 0)
cfg.define('song-status', 'now playing: %(artist)s - %(title)s on "%(album)s" (duration: %(time)s)')

class MPDError(Exception): pass

class MPDDict(dict):
    def __getitem__(self, item):
        if not dict.has_key(self, item):
            return '?'
        else:
            return dict.__getitem__(self, item)

class MPDWatcher(Pdod):
    def __init__(self):
        Pdod.__init__(self, os.path.join(datadir + os.sep + 'plugs' + os.sep + 'mpd', 'mpd'))
        self.running = False
        self.lastsong = -1

    def add(self, bot, ievent):
        if not self.has_key2(bot.name, ievent.channel):
            self.set(bot.name, ievent.channel, True)
            self.save()

    def remove(self, bot, ievent):
        if self.has_key2(bot.name, ievent.channel):
            del self.data[bot.name][ievent.channel]
            self.save()

    def start(self):
        self.running = True
        start_new_thread(self.watch, ())

    def stop(self):
        self.running = False

    def watch(self):
        if not cfg.get('watcher-enabled'):
            raise MPDError('watcher not enabled, use "!%s-cfg watcher-enabled 1" to enable' % os.path.basename(__file__)[:-3])
        while self.running:
            if self.data:
                try:
                    status = MPDDict(mpd('currentsong'))
                    songid = int(status['id'])
                    if songid != self.lastsong:
                        self.lastsong = songid
                        self.announce(status)
                except MPDError:
                    pass
                except KeyError:
                    pass
            time.sleep(cfg.get('watcher-interval'))

    def announce(self, status):
        if not self.running or not cfg.get('watcher-enabled'):
            return
        rlog(5, 'mpd', 'announcing song information')
        status['time'] = mpd_duration(status['time'])
        song = cfg.get('song-status') % status
        for name in self.data.keys():
            bot = fleet.byname(name)
            if bot:
                for channel in self.data[name].keys():
                    bot.say(channel, song)

watcher = MPDWatcher()
if not watcher.data:
    watcher = MPDWatcher()

def init():
    if cfg.get('watcher-enabled'):
        watcher.start()
    return 1

def shutdown():
    if watcher.running:
        watcher.stop()
    return 1

def mpd(command):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(cfg.get('socket-timeout'))
        s.connect((cfg.get('server-host'), cfg.get('server-port')))
    except socket.error, e:
        raise MPDError, 'Failed to connect to server: %s' % str(e)
    m = s.makefile('r')
    l = m.readline()
    if not l.startswith('OK MPD '):
	s.close()
	raise MPDError, 'Protocol error'
    if cfg.get('server-pass') and cfg.get('server-pass') != 'off':
        s.send('password %s\n' % cfg.get('server-pass'))
        l = m.readline()
        if not l.startswith('OK'):
            s.close()
            raise MPDError, 'Protocol error'
    s.send('%s\n' % command)
    s.send('close\n')
    d = []
    while True:
        l = m.readline().strip()
        if not l or l == 'OK':
            break
        if ': ' in l:
            l = l.split(': ', 1)
            l[0] = l[0].lower()
            d.append(tuple(l))
    s.close()
    return d

def mpd_duration(timespec):
    try:
        timespec = int(timespec)
    except ValueError:
        return 'unknown'
    timestr  = ''
    m = 60
    h = m * 60
    d = h * 24
    w = d * 7
    if timespec > w:
        w, timespec = divmod(timespec, w)
        timestr = timestr + '%02dw' % w
    if timespec > d:
        d, timespec = divmod(timespec, d)
        timestr = timestr + '%02dd' % d
    if timespec > h:
        h, timespec = divmod(timespec, h)
        timestr = timestr + '%02dh' % h
    if timespec > m:
        m, timespec = divmod(timespec, m)
        timestr = timestr + '%02dm' % m
    return timestr + '%02ds' % timespec

def handle_mpd_np(bot, ievent):
    try:
        status = MPDDict(mpd('currentsong'))
        status['time'] = mpd_duration(status['time'])
        ievent.reply(cfg.get('song-status') % status)
    except MPDError, e:
        ievent.reply(str(e))

def handle_mpd_simple_seek(bot, ievent, command):
    try:
        mpd(command)
        handle_mpd_np(bot, ievent)
    except MPDError, e:
        ievent.reply(str(e))
        
handle_mpd_next = lambda b,i: handle_mpd_simple_seek(b,i,'next') 
handle_mpd_prev = lambda b,i: handle_mpd_simple_seek(b,i,'prev') 
handle_mpd_play = lambda b,i: handle_mpd_simple_seek(b,i,'play') 
handle_mpd_stop = lambda b,i: handle_mpd_simple_seek(b,i,'stop') 
handle_mpd_pause = lambda b,i: handle_mpd_simple_seek(b,i,'stop') 

def handle_mpd_find(bot, ievent):
    type = 'title'
    args = ievent.args
    if args and args[0].lower() in ['title', 'album', 'artist']:
        type = args[0].lower()
        args = args[1:]
    if not args:
        ievent.missing('[<type>] <what>')
        return
    try:
        find = mpd('search %s "%s"' % (type, ' '.join(args)))
        show = []
        for item, value in find:
            if item == 'file':
                show.append(value)
        if show:
            ievent.reply(show, dot=True, nritems=True)
        else:
            ievent.reply('no result')
    except MPDError, e:
        ievent.reply(str(e))

def handle_mpd_queue(bot, ievent):
    if not ievent.args:
        ievent.missing('<file>')
        return
    try:
        addid = MPDDict(mpd('addid "%s"' % ievent.rest))
        if not addid.has_key('id'):
            ievent.reply('failed to load song "%s"' % ievent.rest)
        else:
            ievent.reply('added song with id "%s", use "mpd-jump %s" to start playback' % (addid['id'], addid['id']))
    except MPDError, e:
        ievent.reply(str(e))

def handle_mpd_jump(bot, ievent):
    pos = 0
    try:    pos = int(ievent.args[0])
    except: pass
    if not pos:
        ievent.missing('<playlist id>')
        return
    try:
        mpd('playid %d' % pos)
        handle_mpd_np(bot, ievent)
    except MPDError, e:
        ievent.reply(str(e))

def handle_mpd_stats(bot, ievent):
    try:
        status = MPDDict(mpd('stats'))
        status['total playtime'] = mpd_duration(status['playtime'])
        status['total database playtime'] = mpd_duration(status['db_playtime'])
        status['uptime'] = mpd_duration(status['uptime'])
        del status['playtime']
        del status['db_playtime']
        del status['db_update']
        result = []
        for item in sorted(status.keys()):
            result.append('%s: %s' % (item, status[item]))
        ievent.reply(result, dot=True)
    except MPDError, e:
        ievent.reply(str(e))

def handle_mpd_watch_start(bot, ievent):
    if not cfg.get('watcher-enabled'):
        ievent.reply('watcher not enabled, use "!%s-cfg watcher-enabled 1" to enable and reload the plugin' % os.path.basename(__file__)[:-3])
        return
    watcher.add(bot, ievent)
    ievent.reply('ok')

def handle_mpd_watch_stop(bot, ievent):
    if not cfg.get('watcher-enabled'):
        ievent.reply('watcher not enabled, use "!%s-cfg watcher-enabled 1" to enable and reload the plugin' % os.path.basename(__file__)[:-3])
        return
    watcher.remove(bot, ievent)
    ievent.reply('ok')

def handle_mpd_watch_list(bot, ievent):
    if not cfg.get('watcher-enabled'):
        ievent.reply('watcher not enabled, use "!%s-cfg watcher-enabled 1" to enable and reload the plugin' % os.path.basename(__file__)[:-3])
        return
    result = []
    for name in sorted(watcher.data.keys()):
        if watcher.data[name]:
            result.append('on %s:' % name)
        for channel in sorted(watcher.data[name].keys()):
            result.append(channel)
    if result:
        ievent.reply(' '.join(result))
    else:
        ievent.reply('no watchers running')

aliases.data['np'] = 'mpd-np'
aliases.data['mpd-search'] = 'mpd-find'
aliases.data['mpd-playid'] = 'mpd-jump'
aliases.data['mpd-watch'] = 'mpd-watch-start'
aliases.data['mpd-stfu'] = 'mpd-watch-stop'
cmnds.add('mpd-np',    handle_mpd_np,    'USER')
cmnds.add('mpd-next',  handle_mpd_next,  'MPD')
cmnds.add('mpd-prev',  handle_mpd_prev,  'MPD')
cmnds.add('mpd-play',  handle_mpd_play,  'MPD')
cmnds.add('mpd-stop',  handle_mpd_stop,  'MPD')
cmnds.add('mpd-pause', handle_mpd_pause, 'MPD')
cmnds.add('mpd-find',  handle_mpd_find,  'MPD')
examples.add('mpd-find', 'search for a song', 'mpd-find title love')
cmnds.add('mpd-queue', handle_mpd_queue, 'MPD')
examples.add('mpd-queue', 'add a song to the playlist', 'mpd-queue mp3/jungle/roni size/roni size-brown paper bag.mp3')
cmnds.add('mpd-jump',  handle_mpd_jump,  'MPD')
examples.add('mpd-jump', 'jump to the specified playlist id', 'mpd-jump 666')
cmnds.add('mpd-stats', handle_mpd_stats, 'USER')
examples.add('mpd-stats', 'show statistics', 'mpd-stats')
cmnds.add('mpd-watch-start', handle_mpd_watch_start, 'MPD')
cmnds.add('mpd-watch-stop',  handle_mpd_watch_stop, 'MPD')
cmnds.add('mpd-watch-list',  handle_mpd_watch_list, 'MPD')

