# gozerplugs/bash.py
#
# bash.org / qdb.us fetcher

""" show quotes from bash.org """

from gozerbot.commands import cmnds
from gozerbot.generic import geturl2, striphtml
from gozerbot.plughelp import plughelp
import re

plughelp.add('bash', 'shows bash.org quotes')

re_p = re.compile('<p class="qt">(.*)</p>', )

def fetch(server, qid='random'):
    html = geturl2('http://%s/%s' % (server, qid))
    text = ''
    keep = False
    for line in html.splitlines():
        if len(line.split('</p>')) == 3:
            return striphtml(line.split('</p>')[1])
        elif line.startswith('<p class="quote">'):
            if '<p class="qt">' in line:
                if line.endswith('</p>'):
                    return striphtml(re_p.findall(line)[0])
                else:
                    text = line.split('<p class="qt">')[1]
                    keep = True
        elif keep:
            if '</p>' in line:
                text = text + line.split('</p>')[0]
                return striphtml(text.replace('<br />', ' '))
            else:
                text = text + line
    if text:
        return striphtml(text.replace('<br />', ' '))
    else:
        return 'no result'

def handle_bash(bot, ievent):
    if ievent.args:
        if not ievent.args[0].isdigit():
            ievent.missing('<id>')
            return
        qid = ievent.args[0]
    else:
        qid = 'random'
    ievent.reply(fetch('bash.org', '?%s' % qid))

cmnds.add('bash', handle_bash, 'USER')
