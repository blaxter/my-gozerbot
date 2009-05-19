# Simple threaded whois lookup tool
# (c) 2008 Wijnand 'maze' Modderman - http://tehmaze.com/
# BSD Licsense

__author__   = "Wijnand 'maze' Modderman"
__licsense__ = "BSD"

import socket
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
import gozerbot.threads.thr as thr

plughelp.add('whois', 'query a whois server')

def do_whois(ievent, server, port, lookup):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((server, port))
        sock.send('%s\r\n' % lookup)
        rock = sock.makefile('rb')
        info = []
        for line in rock.readlines():
            line = line.strip()
            if not line: continue
            if not line.startswith('%'):
                while '  ' in line: line = line.replace('  ', ' ')
                info.append(line)
        sock.close()
        if info:
            ievent.reply(info, dot=', ')
        else:
            ievent.reply('object not found')
    except socket.error, e:
        ievent.reply('socket error: %s' % (str(e),))
    except Exception, e:
        ievent.reply('error: %s' % (str(e),))

def handle_whois(bot, ievent):
    lookup, server, port = None, None, 43
    try:
        if ':' in ievent.args[0]:
            server, port = ievent.args[0].split(':')
            port = int(port)
        else:
            server = ievent.args[0]
        lookup = ievent.args[1]
    except (IndexError, ValueError):
        ievent.missing('<server[:port]> <object>')

    #ievent.reply('doing lookup for "%s" on %s:%d' % (lookup, server, port))
    thr.start_new_thread(do_whois, (ievent, server, port, lookup))

cmnds.add('whois', handle_whois, 'USER')
examples.add('whois', 'do a whois lookup on the specified server', 'whois whois.arin.net AS112')

