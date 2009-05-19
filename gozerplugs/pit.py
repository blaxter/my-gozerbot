# http://paste-it.net client for gozerbot (trough pipes)
# Wijnand 'tehmaze' Modderman - http://tehmaze.com
# BSD License

from gozerbot.commands import cmnds
from gozerbot.config import config
from gozerbot.generic import useragent, waitforqueue
from gozerbot.plughelp import plughelp
from gozerbot.persist.persistconfig import PersistConfig
import copy
import optparse
import urllib
import urllib2

cfg = PersistConfig()
cfg.define('url', 'http://www.paste-it.net/ajax/pit/')
cfg.define('expiry', 604800)
cfg.define('items', 50)
cfg.define('waitforqueue', 50)
cfg.define('useragent', 'paste-it.net command line client (Compatible; %s)' % ' '.join(config['version'].split()[0:2]))

plughelp.add('pit', 'http://www.paste-it.net paste functionality')

class PitOptionParser(optparse.OptionParser):
    def __init__(self, ievent):
        optparse.OptionParser.__init__(self)
        self.ievent = ievent
        self.ievent.stop = False
        self.formatter = optparse.IndentedHelpFormatter(0, 24, None, 1)
        self.formatter.set_parser(self)

    # no wai!
    def exit(self, status=0, msg=None):
        pass

    def error(self, msg):
        if msg:
            self.ievent.reply(msg)
            self.ievent.stop = True

    def format_epilog(self, formatter):
        return formatter.format_epilog(self.epilog)

    def print_help(self, file=None):
        result = []
        for option in self.option_list: 
            result.append('%s: %s' % (', '.join(option._short_opts+option._long_opts), option.help))
        self.ievent.reply(' .. '.join(result))
        self.ievent.stop = True

def handle_pit(bot, ievent):
    if not ievent.inqueue:
        ievent.reply('use pit in a pipeline')
        return
    result = waitforqueue(ievent.inqueue, cfg.get('waitforqueue'), cfg.get('items'))
    if not result:
        ievent.reply('no data to paste')
    # parse options
    pit_parser = PitOptionParser(ievent)
    pit_parser.add_option("-p", "--public", dest="public", action="store_true", default=False, help="make paste public")
    pit_parser.add_option("-s", "--subject", dest="subject", action="store", default="", help="set subject")
    pit_parser.add_option("-e", "--expiry", dest="expiry", action="store", type="int", default=cfg.get('expiry'), help="expiry in seconds")
    pit_parser.add_option("-x", "--syntax", dest="syntax", action="store", default="", help="syntax highlighting")
    (options, args) = pit_parser.parse_args(ievent.rest.split())
    if pit_parser.ievent.stop:
        return
    # interpret options
    postarray = [
        ('content', '\n'.join(result)),
        ('nickname', ievent.nick),
        ('subject', options.subject),
        ('syntax', options.syntax),
        ('expiry', options.expiry),
        ]
    # public paste?
    if options.public:
        postarray.append(("obscure","n"))
    else:
        postarray.append(("obscure","y"))
    postdata = urllib.urlencode(postarray)
    req = urllib2.Request(url=cfg.get('url'), data=postdata)
    req.add_header('User-agent', cfg.get('useragent'))
    ievent.reply(urllib2.urlopen(req).read())

cmnds.add('pit', handle_pit, 'USER')
