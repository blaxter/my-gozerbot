# plugs/probe.py
#
#

""" check if host:port is open """

__copyright__ = 'this file is in the public domain'

from gozerbot.commands import cmnds
from gozerbot.plughelp import plughelp
from gozerbot.examples import examples
import socket

plughelp.add('probe', 'show if host:port is open')

def handle_probe(bot, ievent):
    """ probe <host> <port> .. check if host:port is open """
    try:
        (host, port) = ievent.args
        port = int(port)
    except ValueError:
        ievent.missing('<host> <port>')
        return
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((host, port))
        sock.close()
    except socket.timeout:
        ievent.reply('%s:%s is not up' % (host, port))
        return
    except Exception, ex:
        ievent.reply('%s:%s is not up ==>  %s' % (host, port, str(ex)))
        return
    ievent.reply('%s:%s is up' % (host, port))

cmnds.add('probe', handle_probe, ['OPER', 'PROBE'])
examples.add('probe', 'probe <host> <port> // show if host:port is open', \
'probe gozerbot.org 8088')
