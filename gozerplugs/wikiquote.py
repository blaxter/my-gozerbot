# plugs/wikiquote.py
#
#

""" query wikiquote """

__copyright__ = 'this file is in the public domain'
__revision__ = '$Id: wikiquote.py 517 2007-02-04 16:13:00Z deck $'

from gozerbot.generic import geturl, striphtml, splittxt
from gozerbot.commands import cmnds
from gozerbot.aliases import aliases
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
import re, random

plughelp.add('wikiquote', 'fetch a wikipedia quote')

wikire = re.compile('start content(.*?)end content', re.M)

def handle_wikiquote(bot, ievent):
    """ wikiquote <what> .. search wikiquote for <what> """
    if not ievent.rest:
        ievent.missing('<what>')
        return
    what = ""
    lang = 'en'
    for i in ievent.rest.split():
        first = i[0].upper()
        rest = i[1:]
        if i.startswith('-'):
            if len(i) != 3:
                ievent.reply('invalid option')
                return
            lang = i[1:]
            continue
        what += "%s%s " % (first, rest)
    what = what.strip().replace(' ', '_')
    url = 'http://%s.wikiquote.org/w/wiki.phtml?title=%s' % (lang, what)
    result = geturl(url)
    if not result:
        ievent.reply("can't find data for %s" % what)
        return
    result = result.replace('\n', ' ')
    result = re.sub('\s+', ' ', result)
    regresult = re.search(wikire, result)
    if not regresult:
        ievent.reply("can't match regular expression %s" % url)
        return
    txt = regresult.groups()[0]
    try:
        res = re.sub('\[.*?\]', '', striphtml(random.choice(re.findall('<li>(.*?)</li>',txt))))
    except IndexError:
        ievent.reply("can't find quote")
        return
    ievent.reply(res)

cmnds.add('wikiquote', handle_wikiquote, 'USER')
examples.add('wikiquote', 'wikiquote ["-" <countrycode>] <what> .. search \
wikiquote for <what>','1) wikiquote george bush 2) wikiquote -nl Balkenende')
aliases.data['wquote'] = 'wikiquote'
