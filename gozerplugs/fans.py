# gozerplugs/fans.py
#
#

__depend__ = ['karma', ]

from gozerbot.aliases import aliases
from gozerbot.commands import cmnds
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
from gozerplugs.karma import karma
import shlex

plughelp.add('fans', 'show the lovers and haters of a karma item')

cfg = PersistConfig()
cfg.define('dehighlight', 1)

def dehighlight(nick):
    l = len(nick)
    if l > 1:
        return nick[0:l//2] + '\x030\x03' + nick[l//2:]
    else:
        return nick

def getkarma(item):
    nicks = {}
    ups = karma.getwhoup(item) or []
    dns = karma.getwhodown(item) or []
    nicks = dict((x, 0) for x in set(ups+dns))
    for nick in ups: nicks[nick] += 1
    for nick in dns: nicks[nick] -= 1
    return nicks

def handle_fans(bot, ievent):
    if ievent.args:
        who = ' '.join(ievent.args)
    else:
        who = ievent.nick
    users = getkarma(who)
    fans = sorted(x for x in users if users[x] > 0)
    if fans:
        if cfg.get('dehighlight'): fans = map(dehighlight, fans)
        ievent.reply('the fanclub of %s consists of: ' % (who,), fans, dot=', ')
    else:
        ievent.reply('%s has no fans' % who)

def handle_haters(bot, ievent):
    if ievent.args:
        who = ' '.join(ievent.args)
    else:
        who = ievent.nick
    users = getkarma(who)
    hate = sorted(x for x in users if users[x] < 0)
    if hate:
        if cfg.get('dehighlight'): hate = map(dehighlight, hate)
        ievent.reply('the hateclub of %s consists of: ' % (who,), hate, dot=', ')
    else:
        ievent.reply('%s has no haters' % who)

def handle_vs(bot, ievent):
    lex = shlex.shlex(ievent.rest, posix=False)
    try:
        args = [x.replace('\x00', '') for x in shlex.split(ievent.rest)]
    except ValueError, e:
        ievent.reply(str(e))
        return
    if len(args) < 2:
        ievent.missing('<item1> <item2> [...<itemX>]')
    else:
        items = list(reversed(sorted((karma.get(x), x) for x in args)))
        karmas = []
        for x in xrange(0, len(items)):
            if karmas:
                if items[x][0] == items[x-1][0]:
                    karmas.append('==')
                else:
                    karmas.append('>')
            karmas.append(items[x][1])
        ievent.reply(' '.join(karmas))

cmnds.add('fans', handle_fans, 'USER')
examples.add('fans', 'show fans of karma item', 'fans gozerbot')
aliases.data['love'] = 'fans'
cmnds.add('haters', handle_haters, 'USER')
examples.add('haters', 'show haters of karma item', 'haters gozerbot')
aliases.data['hate'] = 'haters'
cmnds.add('karma-vs', handle_vs, 'USER')
examples.add('vs', 'show lovers versus haters of a karma item', 'gozerbot \
vs supybot')
aliases.data['vs'] = 'karma-vs'
