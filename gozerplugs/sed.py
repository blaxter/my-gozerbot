# Description: Performs a sed-like substitution on the last message by the 
#              calling user
# Author: John Hampton <pacopablo@pacopablo.com>
# Website: http://pacopablo.com
# License: BSD

__author__ = 'John Hampton <pacopablo@pacopablo.com>'
__license__ = "BSD"

# Standard Library Imports
import os
import time
import re

# Third Party Imports

# Local Imports
from gozerbot.callbacks import callbacks
from gozerbot.commands import cmnds
from gozerbot.datadir import datadir
from gozerbot.persist.pdod import Pdod
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.plughelp import plughelp
from gozerbot.examples import examples
from gozerbot.redispatcher import rebefore

plughelp.add('sed', 'Perform substitution on last message spoken')

cfg = PersistConfig()
cfg.define('cmd_req', 0)
sed_expression = r'^s([/|#.:;])(.*?)\1(.*?)\1?([gi]*)$'
sedre = re.compile(sed_expression)

class LastLine(Pdod):
    def __init__(self):
        self.datadir = os.path.join(datadir, 'plugs', 'sed')
        Pdod.__init__(self, os.path.join(self.datadir, 'sed.data'))
        if not self.data:
            self.data = {}

    def handle_sed(self, bot, ievent):
        """ Perform substitution """
        channel = ievent.channel.lower()
        nick = ievent.nick.lower()
        try:
            (delim, broke, fix, flags) = ievent.groups
        except ValueError:
            ievent.missing('<delim><broke><delim><fix><delim>')
            return
        try:
            source = self.data[channel][nick]
            if 'g' in flags:
                count = 0
            else:
                count = 1
            if 'i' in flags:
                broke = '(?i)'+broke
            new_text = re.sub(broke, fix, source, count)

            if source != new_text:
                ievent.reply("%s meant: %s" % (nick, new_text))
                return
        except KeyError:
            bot.say(nick, 'I wasn\'t listening to you.  Try saying something first.')
            return
        except Exception, ex:
            bot.say(nick, 'Error processing regex: %s' % str(ex))
            return

    def precb(self, bot, ievent):
        if not ievent.usercmnd:
            return 1

    def privmsgcb(self, bot, ievent):
        channel = ievent.channel.lower()
        nick = ievent.nick.lower()
        regex = sedre.match(ievent.origtxt)
        if not cfg.get('cmd_req') and regex:
            try:
                (delim, broke, fix, flags) = regex.groups()
            except ValueError:
                return
            try:
                source = self.data[channel][nick]
                if 'g' in flags:
                    count = 0
                else:
                    count = 1
                if 'i' in flags:
                    broke = '(?i)'+broke
                new_text = re.sub(broke, fix, source, count)
                if source != new_text:
                    ievent.reply("%s meant: %s" % (nick, new_text))
                    return

            except KeyError:
                return
            except Exception, ex:
                ievent.reply('Error processing regex: %s' % str(ex))
        self.data.setdefault(channel, {})
        self.data[channel][nick] = ievent.origtxt

def handle_sed(bot, ievent):
    global lastline
    lastline.handle_sed(bot, ievent)

def init():
    global lastline
    lastline = LastLine()
    callbacks.add('PRIVMSG', lastline.privmsgcb, lastline.precb)
    rebefore.add(10, sed_expression, handle_sed, 'USER', allowqueue=False)
    examples.add('s', 'Perform substitution on last message spoken.', 's/foo/bar/')
    return 1

def shutdown():
    lastline.save()
    
