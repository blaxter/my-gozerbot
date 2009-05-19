# tvrage.com serie lookup
# Wijnand 'tehmaze' Modderman - http://tehmaze.com
# BSD License

import re
from gozerbot.commands import cmnds
from gozerbot.generic import geturl
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp

plughelp.add('serie', 'tvrage.com serie lookup')

class Serie:

    base_url = 'http://www.tvrage.com/'
    re_date = re.compile('(\w{3}/\d{2}/\d{4})')
    name_filter = 'abcdefghijklmnopqrstuvwxyz0123456789 '

    def __init__(self, name):
        self.name = self.fix_name(name)

    def fix_name(self, name):
        name  = ''.join([x for x in name if x.lower() in self.name_filter])
        parts = name.split()
        for x in range(0, len(parts)):
            part = parts[x]
            fixed = ''
            if len(part) >= 1:
                fixed = parts[x].upper()[0]
            if len(part) >= 2:
                fixed = fixed + parts[x].lower()[1:]
            parts[x] = fixed
        return '_'.join(parts)

    def fetch(self):
        meta = {}
        data = geturl(self.base_url + self.name)
        for line in data.splitlines():
            try:
                if 'Latest Episode:' in line and not meta.has_key('last ep'):
                    meta['last ep'] = line.split('>')[14].split('</a')[0].split("'")[1].split('/')[-1]
                    test_date = self.re_date.search(line)
                    if test_date:
                        meta['last ep'] = '%s (aired %s)' % (meta['last ep'], test_date.group(1))
                elif 'Next Episode:' in line and not meta.has_key('next ep'):
                    meta['next ep'] = line.split('>')[7].split('</a')[0].split("'")[1].split('/')[-1]
                    test_date = self.re_date.search(line)
                    if test_date:
                        meta['next ep'] = '%s (airs %s)' % (meta['next ep'], test_date.group(1))
                elif 'Genre:' in line and not meta.has_key('genre'):
                    meta['genre'] = line.split('>')[6].split('</td')[0]
                elif 'Status:' in line and not meta.has_key('status'):
                    meta['status'] = line.split('>')[6].split('</td')[0]
                elif 'Runtime:' in line and not meta.has_key('runtime'):
                    meta['runtime'] = line.split('>')[6].split('</td')[0]
            except IndexError:
                pass
        meta = meta.items()
        meta.sort()
        return meta

def handle_serie(bot, ievent):
    if not ievent.args:
        ievent.missing('<serie name>')
        return
    serie = Serie(' '.join(ievent.args))
    info = serie.fetch()
    if info:
        ievent.reply(', '.join(['%s: %s' % (k, v) for (k, v) in info]))
    else:
        ievent.reply('nothing found')

cmnds.add('serie', handle_serie, 'USER')
examples.add('serie', 'search for new episodes', 'serie neighbours')
