# gozerplugs/banner.py
#
# Description: check is host:port is open, and supply the first line or 'banner'
# Author: Wijnand 'tehmaze' Modderman
# Licsense: BSD

""" show banner of <host> <port> """

__author__ = "Wijnand 'tehmaze' Modderman"
__license__ = "BSD"

from gozerbot.commands import cmnds
from gozerbot.plughelp import plughelp
from gozerbot.examples import examples
from gozerbot.tests import tests
import socket

plughelp.add('banner', 'show if host:port is open')

def handle_banner(bot, ievent):
    """ banner <host> <port> .. check if host:port is open """
    try:
        (host, port) = ievent.args
        port = int(port)
    except ValueError:
        ievent.missing('<host> <port>')
        return
    banner = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((host, port))
    except socket.timeout:
        ievent.reply('%s:%s is not up' % (host, port))
        return
    except Exception, ex:
        ievent.reply('%s:%s is not up ==>  %s' % (host, port, str(ex)))
        return
    try:
        msock = sock.makefile()
        banner = msock.readline()
    except:
        pass
    try:
        sock.close()
    except socket.error:
        pass
    if banner:
        ievent.reply('%s:%s is up: %s' % (host, port, banner))
    else:
        ievent.reply('%s:%s is up' % (host, port))

cmnds.add('banner', handle_banner, 'USER')
examples.add('banner', 'banner <host> <port> // show if host:port is open', \
'banner gozerbot.org 25')
tests.add('banner gozerbot.org 25', 'up')
