# plugs/event.py
#
#

""" manage events """

__copyright__ = 'this file is in the public domain'
__gendocfirst__ = ['event.add', ]
__gendoclast__ = ['event-del', ]

from gozerbot.utils.generic import convertpickle
from gozerbot.persist.persist import PlugPersist
from gozerbot.datadir import datadir
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
import os

plughelp.add('event', 'manage events and who is joining them .. can paste \
events to topic')

# UPGRADE PART

def upgrade():
    convertpickle(datadir + os.sep + 'old' + os.sep + 'event', datadir + os.sep + 'plugs' + \
os.sep + 'event' + os.sep + 'event')

## END UPGRADE PART

events = PlugPersist('event')
if not events.data:
    events = PlugPersist('event')
    if not events.data:
        events.data = {}

if not events.data.has_key('eventdict'):
    events.data['eventdict'] = {}

def handle_eventadd(bot, ievent):
    """ event-add <description> .. add event """
    if not ievent.rest:
        ievent.missing('<descr>')
        return
    event = {}
    event['descr'] = ievent.rest.strip()
    event['who'] = []
    if not events.data['eventdict'].has_key(ievent.channel):
        events.data['eventdict'][ievent.channel] = []
    events.data['eventdict'][ievent.channel].append(event)
    events.save()
    ievent.reply('event added')
    
cmnds.add('event-add', handle_eventadd, 'USER')
examples.add('event-add', 'add an event', 'event-add party bla')

def handle_eventlist(bot, ievent):
    """ event-list .. show al registered events """
    result = []
    teller = 1
    if not events.data['eventdict'].has_key(ievent.channel):
        ievent.reply('no events')
        return
    for i in events.data['eventdict'][ievent.channel]:
        result.append("%s) %s" % (teller, i['descr']))
        teller += 1
    if result:
        ievent.reply('events: ', result, dot=True)
    else:
        ievent.reply('no events')

cmnds.add('event-list', handle_eventlist, 'USER')
examples.add('event-list' , 'show all events', 'event-list')

def handle_eventdel(bot, ievent):
    """ event-del <nr> .. delete event """
    try:
        eventnr = int(ievent.args[0])
    except (IndexError, ValueError):
        ievent.missing('<eventnr>')
        return
    try:
        del events.data['eventdict'][ievent.channel][eventnr-1]
        events.save()
        ievent.reply('event %s deleted' % eventnr)
    except (KeyError, IndexError):
        ievent.reply("can't delete eventnr %s" % eventnr)

cmnds.add('event-del', handle_eventdel, ['EVENT', 'OPER'])
examples.add('event-del', 'delete event', 'event-del 2')

def handle_eventjoin(bot, ievent):
    """ event-join <nr> .. join an event .. add nick to eventlist"""
    try:
        eventnr = int(ievent.args[0])
    except (IndexError, ValueError):
        ievent.missing('<eventnr>')
        return
    try:
        if ievent.nick in events.data['eventdict'][ievent.channel][eventnr-1]\
['who']:
            ievent.reply('%s is already joined' % ievent.nick)
            return
        events.data['eventdict'][ievent.channel][eventnr-1]['who'].\
append(ievent.nick)
        events.save()
        ievent.reply('%s added to event %s ' % (ievent.nick, eventnr))
    except (KeyError, IndexError):
        ievent.reply("can't add %s to event %s" % (ievent.nick, eventnr))

cmnds.add('event-join', handle_eventjoin, 'USER')
examples.add('event-join', 'join an event', 'event-join 2')

def handle_eventadduser(bot, ievent):
    """ event-adduser <nr> <nick> .. add nick to eventlist"""
    try:
        eventnr, nick = int(ievent.args[0]), ievent.args[1]
    except (IndexError, ValueError):
        ievent.missing('<eventnr>')
        return
    try:
        if nick in events.data['eventdict'][ievent.channel][eventnr-1]\
['who']:
            ievent.reply('%s is already joined' % nick)
            return
        events.data['eventdict'][ievent.channel][eventnr-1]['who'].\
append(nick)
        events.save()
        ievent.reply('%s added to event %s ' % (nick, eventnr))
    except (KeyError, IndexError):
        ievent.reply("can't add %s to event %s" % (nick, eventnr))

cmnds.add('event-adduser', handle_eventadduser, ['OPER', 'EVENT'])
examples.add('event-adduser', 'add nick to an event', 'event-adduser 2 dunk')

def handle_eventpart(bot, ievent):
    """ event-part <nr> .. leave an event .. delete nick from eventlist"""
    try:
        eventnr = int(ievent.args[0])
    except (IndexError, ValueError):
        ievent.missing('<eventnr>')
        return
    try:
        events.data['eventdict'][ievent.channel][eventnr-1]['who'].\
remove(ievent.nick)
        events.save()
        ievent.reply('%s removed from event %s ' % (ievent.nick, eventnr))
    except (KeyError, IndexError, ValueError):
        ievent.reply("can't remove %s from event %s" % (ievent.nick, eventnr))

cmnds.add('event-part', handle_eventpart, 'USER')
examples.add('event-part', 'unsubscribe from an event', 'event-part 2')

def handle_eventwho(bot, ievent):
    """ event-who .. show nicks of people registered to event """
    try:
        eventnr = int(ievent.args[0])
    except (IndexError, ValueError):
        ievent.missing('<eventnr>')
        return
    try:
        who = events.data['eventdict'][ievent.channel][eventnr-1]['who']
        what = events.data['eventdict'][ievent.channel][eventnr-1]['descr']
        if who:
            ievent.reply('%s: ' % what, who, dot=True)
        else:
            ievent.reply('no one joined event %s yet' % eventnr)
    except (KeyError, IndexError):
        ievent.reply("can't get data for event %s" % eventnr)

cmnds.add('event-who', handle_eventwho, 'USER')
examples.add('event-who', 'show who joined an event', 'event-who 2')

def handle_eventremove(bot, ievent):
    """ event-remove <nr> <nick> .. remove <nick> from eventlist """
    try:
        (eventnr, nick) = (int(ievent.args[0]), ievent.args[1])
    except (IndexError, ValueError):
        ievent.missing('<eventnr> <nick>')
        return
    try:
        events.data['eventdict'][ievent.channel][eventnr-1]['who'].remove(nick)
        events.save()
        ievent.reply('%s removed from event %s ' % (nick, eventnr))
    except (KeyError, IndexError, ValueError):
        ievent.reply("can't remove %s from event %s" % (nick, eventnr))

cmnds.add('event-remove', handle_eventremove, ['EVENT', 'OPER'])
examples.add('event-remove', 'delete nick from an event', 'event-remove 3 dunker')

def handle_eventtopic(bot, ievent):
    """ event-topic .. add events to topic """
    if not events.data['eventdict'].has_key(ievent.channel):
        ievent.reply('no events for %s' % ievent.channel)
        return
    topic = bot.gettopic(ievent.channel)
    if topic:
        what = topic[0]
    else:
        what = None
    topicstr = ""
    for i in events.data['eventdict'][ievent.channel]:
        if what and i['descr'] in what:
            continue        
        topicstr += "%s | " % i['descr']
    if not topicstr:
        ievent.reply('no events to set into topic')
        return
    if what:
        totopic = what + ' | ' + topicstr[:-3]
    else:
        totopic = topicstr[:-3]
    bot.send('TOPIC %s :%s' % (ievent.channel, totopic))

cmnds.add('event-topic', handle_eventtopic, ['EVENT', 'OPER'], threaded=True)
examples.add('event-topic', 'put events into the topic', 'event-topic')
