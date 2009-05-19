# plugs/misc.py
#
#

""" misc commands. """

__copyright__ = 'this file is in the public domain'
__gendocfirst__ = ['timezone', 'time']

# gozerbot imports
from gozerbot.generic import waitforuser
from gozerbot.tests import tests
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.aliases import aliases
from gozerbot.plughelp import plughelp
from gozerbot.persist.persiststate import UserState
from gozerbot.users import users

# basic imports
import time, os, threading, thread

plughelp.add('misc', 'miscellaneous commands')

def handle_test(bot, ievent):

    """ test .. give test response which is a string of the ircevent. """

    ievent.reply(str(ievent))

cmnds.add('test', handle_test, ['USER', 'WEB', 'JCOLL', 'CLOUD', ], options={'--t': 'bla'})
examples.add('test', 'give test response',' test')
tests.add('test')

def handle_source(bot, ievent):

    """ source .. show where to fetch the bot source. """ 

    ievent.reply('see http://gozerbot.org')

cmnds.add('source', handle_source, ['USER', 'WEB', 'CLOUD'])
examples.add('source', 'show source url', 'source')
aliases.data['about'] = 'source'
tests.add('source', 'gozerbot')

def handle_response(bot, ievent):

    """ check if we can get a reply of user. """

    ievent.reply("say something so i can see if i can get a \
response from you")
    reply = waitforuser(bot, ievent.userhost)

    if not reply:
        ievent.reply("can't get a response")
    else:
        ievent.reply("you said %s" % reply.txt)

cmnds.add('response', handle_response, ['USER', ], threaded=True)
examples.add('response', 'response test .. see if we can receive a response', 'response')

def handle_time(bot, ievent):

    """ show current time """

    authuser = users.getname(ievent.userhost)

    if authuser:

        if ievent.rest:
            if users.exist(ievent.rest.lower()):
                username = ievent.rest.lower()
            else:
                ievent.reply("We don't have a user %s" % ievent.rest)
                return
        else:
            username = authuser

        userstate = UserState(username)

        try:
            tz = userstate['TZ']
        except KeyError:
            if username == authuser:
                tz = handle_ask_timezone(bot, ievent)
                if tz and set_timezone(bot, ievent, userstate, tz):
                    tz = userstate['TZ']
                else:
                    return
            else:
                ievent.reply("%s doesn't have a timezone set" % username)
                return
        ievent.reply(get_time(tz, username, authuser))

    else:
        ievent.reply(get_time('UTC', '', ''))

cmnds.add('time', handle_time, ['USER', 'CLOUD'], threaded=True)
examples.add('time', 'show current time (of a user)', 'time test')
aliases.data['t'] = 'time'
aliases.data['date'] = 'time'
#tests.add('time')

def handle_timezone(bot, ievent):

    """ timezone .. set current timezone. """

    username = users.getname(ievent.userhost)

    if username:
        userstate = UserState(username)
        if ievent.rest:
            try:
                timezone = int(ievent.rest)
                
                set_timezone(bot, ievent, userstate, timezone)
            except ValueError:
                ievent.reply('TZ needs to be an integer')
                return
        else:
            timezone = handle_ask_timezone(bot, ievent)
            if timezone:
                set_timezone(bot, ievent, userstate, timezone)
            else:
                ievent.reply("can't determine timezone")

cmnds.add('timezone', handle_timezone, ['USER'], threaded=True)
examples.add('timezone', 'set current timezone', 'timezone +1')
#tests.add('timezone')

def handle_ask_timezone(bot, ievent):

    """ ask for a users timezone. """

    ievent.reply('what is your timezone ? for example -1 or +4')
    response = waitforuser(bot, ievent.userhost)

    if response:
        return response.txt
    else:
        ievent.reply("can't determine timezone .. not setting it")
        return

def set_timezone(bot, ievent, userstate, timezone):

    """ set a users timezone. """

    # check for timezone validity and return False, if necessary
    try:
        tz = int(timezone)
    except ValueError:
        ievent.reply('timezone needs to be an integer')
        return False

    userstate['TZ'] = timezone
    userstate.save()
    ievent.reply("timezone set to %s" % timezone)
    return True

def get_time(zone, username, authuser):

    """ get the time of a user. """

    try:
        zone = int(zone)
    except ValueError:
        zone = 0

    return time.ctime(time.time() + int(time.timezone) + zone*3600)
