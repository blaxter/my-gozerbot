# gozerplugs/trac.py
#
#

from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.aliases import aliasset

def handle_tracwiki(bot, ievent):
    if not ievent.rest:
        ievent.missing("<item>")
        return
    ievent.reply('http://trac.edgewall.org/wiki/%s' % ievent.rest)

cmnds.add('trac-wiki', handle_tracwiki, 'USER')
examples.add('trac-wiki', 'give t.e.o wiki url', 'trac-wiki TracAdmin')
aliasset('wiki', 'trac-wiki')
        