# plugs/dns.py
#
# 

__copyright__ = 'this file is in the public domain'

from gozerbot.commands import cmnds
from gozerbot.examples import examples 
from gozerbot.plughelp import plughelp
import copy
import re
import socket

plughelp.add('dns', 'do ip or host lookup')

_re_hexip = re.compile('^[\da-f]{8}$', re.I)

def handle_hostname(bot, ievent):
    """ hostname <ipnr> .. get hostname of ip number"""
    try:
        item = ievent.args[0]
    except IndexError:
        ievent.missing('<ipnr>')
        return
    try:
        hostname = socket.gethostbyaddr(item)
        ievent.reply(hostname[0])
    except:
        ievent.reply("can't match " + str(item))

cmnds.add('host', handle_hostname, 'USER')
examples.add('host', 'get hostname for ip', 'host 194.109.129.219')

def handle_ip(bot, ievent):
    """ ip <hostname> .. get ip of hostname """
    try:
        item = ievent.args[0]
    except IndexError:
        ievent.missing('<hostname>')
        return
    try:
        ipnr = socket.gethostbyname(item)
        ievent.reply(ipnr)
    except:
        ievent.reply("can't match " + str(item))

cmnds.add('ip', handle_ip, 'USER')
examples.add('ip', 'show ip number of host', 'ip gozerbot.org')

def handle_dns(bot, ievent):
    """ <host|ip> performs a DNS lookup an ip or hostname. """
    if not ievent.args:
        ievent.missing('<host | ip>')
    else:
        is_a   = None
        result = None
        # If we support IPv6 ...
        if socket.has_ipv6:
            # ... then check if this is an IPv6 ip
            try:
                socket.inet_pton(socket.AF_INET6, ievent.args[0])
                is_a = 'ipv6'
            except socket.error:
                pass
        # Ah not an IPv6 ip ...
        if not is_a:
            # ... maybe IPv4 ?
            try:
                socket.inet_pton(socket.AF_INET, ievent.args[0])
                is_a = 'ipv4'
            except socket.error:
                pass
        # Not an ip, must be a hostname then
        if not is_a:
            is_a = 'host'
        # If it was an ip ...
        if is_a in ['ipv4', 'ipv6']:
            try:
                # ... try to resolve it
                result = socket.gethostbyaddr(ievent.args[0])
                if result[1]:
                    result = 'primary: %s, aliases: %s' % \
                        (result[0], ', '.join(result[1]))
                else:
                    result = result[0]
                ievent.reply('%s ip %s resolves to %s' % \
                    (is_a, ievent.args[0], result))
            except Exception, e:
                ievent.reply('could not resolve %s address %s: %s' % \
                    (is_a, ievent.args[0], e[1]))
        # Oh it's a host, lets resolve that
        elif is_a == 'host':
            try:
                result = []
                for info in socket.getaddrinfo(ievent.args[0], None):
                    if info[0] in [socket.AF_INET, socket.AF_INET6] and \
                        info[1] == socket.SOCK_STREAM:
                        ip = info[4][0]
                        if not ip in result:
                            result.append(ip)
                if not result:
                    ievent.reply('could not resolve hostname %s: not found' % \
ievent.args[0])
                else:
                    ievent.reply('%s resolves to: %s' % (ievent.args[0], \
', '.join(result)))
            except Exception, e:
                ievent.reply('could not resolve hostname %s: %s' % \
                    (ievent.args[0], e[1]))
        else:
            ievent.reply('lookup failed, no valid data found')

cmnds.add('dns', handle_dns, 'USER')
examples.add('dns', 'look up an ip or hostname', 'dns gozerbot.org')

def handle_hexip(bot, ievent):
    """ <ip|hex ip> returns the reverse of the given argument. """
    if not ievent.args:
        return ievent.missing('<ip | hex ip>')
    is_a = None
    if _re_hexip.match(ievent.args[0]):
        is_a = 'hexip'
    else:
        try:
            socket.inet_pton(socket.AF_INET, ievent.args[0])
            is_a = 'defip'
        except socket.error:
            pass
    if not is_a:
        ievent.missing('<ip | hex ip>')
        return
    if is_a == 'hexip':
        ip = []
        for i in range(4):
            ip.append(str(int(ievent.args[0][i*2:i*2+2], 16)))
        ip = '.'.join(ip)
        nevent = copy.copy(ievent)
        nevent.args = [ip]
        handle_dns(bot, nevent)
    else:
        test = ievent.args[0].split('.')
        ip = 16777216 * int(test[0]) + 65536 * int(test[1]) + 256 * \
int(test[2]) + int(test[3])
        ievent.reply('ip %s = %08x' % (ievent.args[0], ip))

cmnds.add('hexip', handle_hexip, 'USER')
examples.add('hexip', 'return the hex ip notation of an ip, or vice versa', \
'hexip 7F000001')
