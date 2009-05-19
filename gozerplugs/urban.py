# plugs/urban.py
#
#

""" query urbandictionary """

__copyright__ = 'this file is in the public domain'
__author__ = "Bas van Oostveen"

from gozerbot.generic import geturl, striphtml, splittxt
from gozerbot.commands import cmnds
from gozerbot.aliases import aliases
from gozerbot.examples import examples
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.plughelp import plughelp

plughelp.add('urban', 'query the urban server')

import re
try:
    import SOAPpy
    __has_soap = True
except ImportError:
    __has_soap = False

__version__ = "1.0"

cfg = PersistConfig()
cfg.define('key', "")
cfg.define('url', "http://api.urbandictionary.com/soap")

def check_requirements(func):
    def wrap(bot, ievent):
	def show_error(msg):
	    """ urban show error message """
	    ievent.reply(msg)
	if not __has_soap:
	    return show_error("You need to install python-soappy for this plugin, on debian/ubuntu you can use apt-get install python-soappy")
	if not len(cfg.data['key'])==32:
	    return show_error("You need to set a license key with !urban-cfg key <my_license_key> from http://www.urbandictionary.org/api.php")
	return func(bot, ievent)
    return wrap

@check_requirements
def handle_urban(bot, ievent):
    """ urban <what> .. search urban for <what> """
    if not ievent.rest:
        ievent.missing('<search query>')
        return
    opt, url, what = "", "", ievent.rest.strip()
    if what[0]=="-":
	opt, what = what.split(" ", 1)
    try:
	server = SOAPpy.SOAPProxy(cfg.data['url'])
	results = server.lookup(cfg.data['key'], what)
	format = lambda item: (item.word, item.definition.replace("\n", "").strip())
	res = [": ".join(format(item)) for item in results]
	if res:
	    if opt=="-url":
		try:
	    	    url = results[0].url.rsplit("&")[0]+" => "
		except:
		    url = ""
	    ievent.reply(url, result=res, dot=True) # dot=" | ")
	else:
	    ievent.reply("word not found: %s" % what)
    except:
	raise

cmnds.add('urban', handle_urban, 'USER')
examples.add('urban', 'urban <what> .. search \
urbandictionary for <what>','1) urban bot 2) urban shizzle')
aliases.data['urbandictionary'] = 'urban'

@check_requirements
def handle_urban_count(bot, ievent):
    """ urban <what> .. count urban entries for <what> """
    if not ievent.rest:
        ievent.missing('<search query>')
        return
    what = ievent.rest.strip()
    try:
	server = SOAPpy.SOAPProxy(cfg.data['url'])
	results = server.count_definitions(cfg.data['key'], what)
	ievent.reply("`%s` has %i urban dictionary entries" % (what, results))
    except:
	raise

cmnds.add('urban-count', handle_urban_count, 'USER')

@check_requirements
def handle_urban_nearby(bot, ievent):
    """ urban <what> .. count urban entries for <what> """
    if not ievent.rest:
        ievent.missing('<search query>')
        return
    what = ievent.rest.strip()
    try:
	server = SOAPpy.SOAPProxy(cfg.data['url'])
	results = server.nearby(cfg.data['key'], what)
	ievent.reply("Words near `%s`: %s" % (what, ' ..'.join(results)))
    except KeyError, e:
	ievent.reply("Error 500: Urban dictionary made a boo boo.")
    except:
	raise

cmnds.add('urban-nearby', handle_urban_nearby, 'USER')

def handle_urban_related(bot, ievent):
    """ urban <what> .. count urban entries for <what> """
    if not ievent.rest:
        ievent.missing('<search query>')
        return
    what = ievent.rest.strip()
    try:
	server = SOAPpy.SOAPProxy(cfg.data['url'])
	results = server.get_related_tags(cfg.data['key'], what)
	ievent.reply("Words related to `%s`: %s" % (what, ' .. '.join(results)))
    except KeyError, e:
	ievent.reply("Error 500: Urban dictionary made a boo boo.")
    except:
	raise

cmnds.add('urban-related', handle_urban_related, 'USER')

@check_requirements
def handle_urban_verifykey(bot, ievent):
    server = SOAPpy.SOAPProxy(cfg.data['url'])
    result = server.verify_key(cfg.data['key'])
    if result:
	ievent.reply("License key is valid")
    else:
	ievent.reply("License key is invalid")
cmnds.add('urban-verifykey', handle_urban_verifykey, 'OPER')

@check_requirements
def handle_urban_random(bot, ievent):
    server = SOAPpy.SOAPProxy(cfg.data['url'])
    result = server.get_random_definition(cfg.data['key'])
    ievent.reply("%(word)s: %(definition)s" % result)
cmnds.add('urban-random', handle_urban_random, 'USER')

@check_requirements
def handle_urban_daily(bot, ievent):
    server = SOAPpy.SOAPProxy(cfg.data['url'])
    result = server.get_daily_definition(cfg.data['key'])
    ievent.reply("%(word)s: %(definition)s" % result)
cmnds.add('urban-daily', handle_urban_daily, 'USER')

def handle_urban_version(bot, ievent):
    ievent.reply("urban plugin version: %s" % __version__)
cmnds.add('urban-version', handle_urban_version, 'OPER')

