# gozerplugs/mash.py
#
#

from gozerbot.generic import geturl, striphtml
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
from simplejson import loads

plughelp.add('mash', 'query searchmash')

baseurl = 'http://www.searchmash.com/results/'

def handle_mash(bot, ievent):
    if not ievent.rest:
        ievent.missing('<what>')
        return
    data = geturl(baseurl + '+'.join(ievent.rest.split()))
    try:
        results = loads(data)
    except ValueError:
        ievent.reply("can't make results of %s" % data)
        return 
    res = []
    for result in results['results']:
        res.append('%s: - <%s>' % (striphtml(result['title']), result['url']))
    ievent.reply('results for %s: ' % ievent.rest, res, dot=' || ')

cmnds.add('mash', handle_mash, 'USER')
examples.add('mash', 'query searchmash', 'mash gozerbot')
