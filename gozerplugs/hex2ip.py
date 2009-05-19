# plugs/hex2ip.py
#
#

from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
import struct, socket

plughelp.add('hex2ip', 'convert a hexadecimal number to an ip addres')

def handle_hex2ip(bot, ievent):
    try:
        what = ievent.args[0]
    except IndexError:
        ievent.missing("<hexnr>")
        return
    try:
        ipint = int(what, 16)
        ipint = socket.ntohl(ipint)
        packed = struct.pack('l', ipint)
        ip = socket.inet_ntoa(str(packed))
    except Exception, ex:
        ievent.reply("can't make ipnr out of %s" % what)
        return
    ievent.reply('%s is %s' % (what, ip))
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except:
        ievent.reply("can't find hostname of %s" % ip)
        return
    ievent.reply('hostname is %s' % hostname)

cmnds.add('hex2ip', handle_hex2ip, 'USER')
examples.add('hex2ip', 'convert hexadecimal number to ip addres', 'hex2ip \
54008c8a')
