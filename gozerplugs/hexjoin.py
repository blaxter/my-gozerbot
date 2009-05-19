# plugs/hexonjoin.py
#
#

from gozerbot.callbacks import callbacks
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.aliases import aliasset
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
import struct, socket

plughelp.add('hexjoin', 'show ip and hostname from user joining a channel')

cfg = PersistConfig()
cfg.define('channels', [])

def hexjoin(bot, ievent):
    what = ievent.user
    ip = None
    try:
        ipint = int(what, 16)
        ipint = socket.ntohl(ipint)
        packed = struct.pack('l', ipint)
        ip = socket.inet_ntoa(str(packed))
    except Exception, ex:
        return
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except:
        if ip:
            bot.say(ievent.channel, '%s is on %s' % (ievent.nick, ip))
            return
    bot.say(ievent.channel, '%s is on %s' % (ievent.nick, hostname))

def prehexjoin(bot , ievent):
    if not len(ievent.user) == 8:
        return 0
    try:
        int(ievent.user, 16)
    except ValueError:
        return 0
    if (bot.name, ievent.channel) in cfg.get('channels'):
        return 1

callbacks.add('JOIN', hexjoin, prehexjoin)

def handle_hexjoinenable(bot, ievent):
    cfg.append('channels', (bot.name, ievent.channel))
    ievent.reply('%s channel added' % ievent.channel)

cmnds.add('hexjoin-enable', handle_hexjoinenable, 'OPER')
examples.add('hexjoin-enable', 'enable hexjoin in the channel the command is \
given in', 'hexjoin-enable')

def handle_hexjoindisable(bot, ievent):
    try:
        cfg.remove('channels', (bot.name, ievent.channel))
        ievent.reply('%s channel removed' % ievent.channel)
    except ValueError:
        ievent.reply('%s channel is not in channels list' % ievent.channel)

cmnds.add('hexjoin-disable', handle_hexjoindisable, 'OPER')
examples.add('hexjoin-disable', 'disable hexjoin in the channel this command \
is given in', 'hexjoin-disable')
