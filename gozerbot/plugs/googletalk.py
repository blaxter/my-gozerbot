# plugs/googletalk.py
#
#

""" enable the bot to log into google chat. """ 

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from gozerbot.callbacks import jcallbacks
from gozerbot.generic import rlog
from gozerbot.config import config
from gozerbot.plughelp import plughelp

plughelp.add('googletalk', 'the google talk plugin make it possible to link \
to the googletalk servers .. google changes the JID of the bot so this \
plugin detects this and sets the bots JID .. for this to work the bot must \
be in a googletalk users buddieslist')

def googletalktest(bot, msg):

    """ check if presence callbacks should fire. """

    if not 'google' in bot.host:
        return 0

    if "vcard-temp:x:update" in str(msg):
        newjid = msg.getAttrs()['to']
        if bot.me != str(newjid):
            if bot.me in str(newjid):
                return 1
        
def googlejidchange(bot, msg):

    """ set bot jid to the google jid. """

    import xmpp
    newjid = msg.getAttrs()['to']
    bot.jid = xmpp.JID(newjid)
    bot.me = str(bot.jid)
    bot.google = True
    rlog(10, 'googletalk', "changed ident to %s" % bot.me)

jcallbacks.add('Presence', googlejidchange, googletalktest)
