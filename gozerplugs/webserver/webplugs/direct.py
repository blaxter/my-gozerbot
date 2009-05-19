# web/dispatch.py
#
#

""" dispatch web request onto the plugins dispatcher """

__copyright__ = 'this file is in the public domain'

from gozerbot.generic import waitforqueue, handle_exception
from gozerbot.fleet import fleet
from gozerbot.irc.ircevent import Ircevent
from gozerbot.plugins import plugins
from gozerbot.threads.thr import start_new_thread
from gozerplugs.webserver.server import httpd
from urllib import unquote_plus
import Queue

def handle_dispatch(event):
    """ dispatch web request """
    input = unquote_plus(event.path)
    bot = fleet.getfirstbot()
    ievent = Ircevent()
    try:
        what = input.split('?', 1)[1]
    except IndexError:
        return ["dispatch what ?", ]
    if what.startswith("command="):
        what = what[8:]
    ievent.txt = what
    ievent.nick = 'web'
    ievent.userhost = 'web@web'
    ievent.channel = 'web'
    q = Queue.Queue()
    ievent.queues.append(q)
    ievent.speed = 3
    ievent.bot = bot
    result = []
    if plugins.woulddispatch(bot, ievent):
        start_new_thread(plugins.trydispatch, (bot, ievent))
    else:
        return ["can't dispatch %s" % what, ]
    result = waitforqueue(q, 60)
    if not result:
        return ["can't dispatch %s" % what, ]
    return result

if httpd:
    httpd.addhandler('/dispatch', handle_dispatch)
