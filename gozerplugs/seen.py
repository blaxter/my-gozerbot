# Description: tracks when a nick is last seen
# Author: Wijnand 'tehmaze' Modderman
# Website: http://tehmaze.com
# License: BSD

from gozerbot.callbacks import callbacks
from gozerbot.commands import cmnds
from gozerbot.datadir import datadir
from gozerbot.persist.pdod import Pdod
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.plughelp import plughelp
from gozerbot.examples import examples
import os, time

plughelp.add('seen', 'remember what people said for the last time')

cfg = PersistConfig()
cfg.define('tz', '+0100')

class Seen(Pdod):
    def __init__(self):
        self.datadir = datadir + os.sep + 'plugs' + os.sep + 'seen'
        Pdod.__init__(self, os.path.join(self.datadir, 'seen.data'))

    def handle_seen(self, bot, ievent):
        if not ievent.args:
            ievent.missing('<nick>')
            return
        nick = ievent.args[0].lower()
        if not self.data.has_key(nick):
            alts = [x for x in self.data.keys() if nick in x]
            if alts:
                alts.sort()
                if len(alts) > 10:
                    nums = len(alts) - 10
                    alts = ', '.join(alts[:10]) + ' + %d others' % nums
                else:
                    alts = ', '.join(alts)
                ievent.reply('no logs for %s, however, I remember seeing: %s' % (nick, alts))
            else:
                ievent.reply('no logs for %s' % nick)
        else:
            text = self.data[nick]['text'] and ': %s' % self.data[nick]['text'] or ''
            ievent.reply('%s was last seen on %s at %s, %s%s' % (nick, self.data[nick]['bot'], 
                time.strftime('%a, %d %b %Y %H:%M:%S '+cfg.get('tz'), time.localtime(self.data[nick]['time'])),
                self.data[nick]['what'], text))

    def privmsgcb(self, bot, ievent):
        self.data[ievent.nick.lower()] = {
            'time':    time.time(),
            'text':    ievent.origtxt,
            'bot':     bot.name,
            'channel': ievent.channel,
            'what':    'saying',
            }

    def joincb(self, bot, ievent):
        self.data[ievent.nick.lower()] = {
            'time':    time.time(),
            'text':    '',
            'bot':     bot.name,
            'channel': ievent.channel,
            'what':    'joining %s' % ievent.channel,
            }
    
    def partcb(self, bot, ievent):
        self.data[ievent.nick.lower()] = {
            'time':    time.time(),
            'text':    ievent.txt,
            'bot':     bot.name,
            'channel': ievent.channel,
            'what':    'parting %s' % ievent.channel,
            }
    
    def quitcb(self, bot, ievent):
        self.data[ievent.nick.lower()] = {
            'time':    time.time(),
            'text':    ievent.txt,
            'bot':     bot.name,
            'channel': ievent.channel,
            'what':    'quitting',
            }
    

    def size(self):
        return len(self.data.keys())

def init():
    global seen
    seen = Seen()
    callbacks.add('PRIVMSG', seen.privmsgcb)
    callbacks.add('JOIN', seen.joincb)
    callbacks.add('PART', seen.partcb)
    callbacks.add('QUIT', seen.quitcb)
    cmnds.add('seen', seen.handle_seen, ['USER', 'CLOUD'])
    examples.add('seen', 'show last spoken txt of <nikc>', 'seen dunker')
    return 1

def shutdown():
    global seen
    seen.save()
    del seen

def size():
    global seen
    return seen.size()
