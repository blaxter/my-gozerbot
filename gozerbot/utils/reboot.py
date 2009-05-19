# gozerbot/utils/reboot.py
#
#

from gozerbot.fleet import fleet
from gozerbot.config import config
from simplejson import dump
import os, sys, pickle, tempfile

def reboot():
    fleet.exit()
    os.execl(sys.argv[0], *sys.argv)

def reboot_stateful(bot, ievent, fleet, partyline):
    """ reboot the bot, but keep the connections """
    config.reload()
    session = {'bots': {}, 'name': bot.name, 'channel': ievent.channel, \
'partyline': []}
    for i in fleet.bots:
        session['bots'].update(i._resumedata())
    session['partyline'] = partyline._resumedata()
    sessionfile = tempfile.mkstemp('-session', 'gozerbot-')[1]
    dump(session, open(sessionfile, 'w'))
    fleet.save()
    fleet.exit(jabber=True)
    os.execl(sys.argv[0], sys.argv[0], '-r', sessionfile)
