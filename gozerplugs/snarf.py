# gozerplugs/plugs/snarf.py
# 
#

__author__ = "Wijnand 'tehmaze' Modderman - http://tehmaze.com"
__license__ = 'BSD'
__gendoclast__ = ['snarf-disable', ]

from gozerbot.callbacks import callbacks, jcallbacks
from gozerbot.plughelp import plughelp
from gozerbot.aliases import aliases
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.generic import decode_html_entities, get_encoding, geturl, \
geturl2, rlog, handle_exception
from gozerbot.persist.persist import Persist
from gozerbot.persist.persistconfig import PersistConfig
import urllib
import urllib2
import urlparse
import copy
import re
import socket

plughelp.add('snarf', 'the snarf plugin gets the title of the web page of \
the provided url or the last url in the log')

cfg           = Persist('snarf', {})
pcfg          = PersistConfig()
pcfg.define('allow', ['text/plain', 'text/html', 'application/xml'])
re_html_title = re.compile(u'<title>(.*)</title>', re.I | re.M | re.S)
re_url_match  = re.compile(u'((?:http|https)://\S+)')
re_html_valid = {
    'result':   re.compile('(Failed validation, \
\d+ errors?|Passed validation)', re.I | re.M),
    'modified': re.compile('<th>Modified:</th>\
<td colspan="2">([^<]+)</td>', re.I | re.M),
    'server':   re.compile('<th>Server:</th>\
<td colspan="2">([^<]+)</td>', re.I | re.M),
    'size':     re.compile('<th>Size:</th><td colspan="2">\
([^<]+)</td>', re.I | re.M),
    'content':  re.compile('<th>Content-Type:</th><td colspan="2">\
([^<]+)</td>', re.I | re.M),
    'encoding': re.compile('<td>([^<]+)</td><td><select name="charset" \
id="charset">', re.I | re.M),
    'doctype':  re.compile('<td>([^<]+)</td><td><select id="doctype" \
name="doctype">', re.I | re.M)
    }
urlcache      = {}
urlvalidate   = 'http://validator.w3.org/check?charset=%%28\
detect+automatically%%29&doctype=Inline&verbose=1&%s'

class SnarfException(Exception):
    pass

def geturl_title(url):
    """ fetch title of url """
    try:
        result = geturl2(url)
    except urllib2.HTTPError, ex:
        rlog(10, 'snarf', str(ex))
        return False
    except urllib2.URLError, ex:
        rlog(10, 'snarf', str(ex))
        return False
    except IOError, ex:
        try:
            errno = ex[0]
        except IndexError:
            handle_exception()
            return
        return False
    if not result:
        return False
    test_title = re_html_title.search(result)
    if test_title:
        # try to find an encoding and standardize it to utf-8
        encoding = get_encoding(result)
        title = test_title.group(1).decode(encoding, 'replace').replace('\n', ' ')
        return decode_html_entities(title)
    return False

def geturl_validate(url):
    """ validate url """
    url = urlvalidate % urllib.urlencode({'uri': url})
    try:
        result = geturl(url)
    except IOError, ex:
        try:
            errno = ex[0]
        except IndexError:
            handle_exception()
            return
        return False
    if not result:
        return False
    results = {}
    for key in re_html_valid.keys():
        results[key] = re_html_valid[key].search(result)
        if results[key]:
            results[key] = results[key].group(1)
        else:
            results[key] = '(unknown)'
    return results

def valid_url(url):
    """ check if url is valid """
    if not re_url_match.match(url):
        return False
    parts = urlparse.urlparse(url)
    # do a HEAD request to get the content-type
    request = urllib2.Request(url)
    request.get_method = lambda: "HEAD"
    content = urllib2.urlopen(request)
    if content.headers['content-type']:
        type = content.headers['content-type'].split(';', 1)[0].strip()
        if type not in pcfg.get('allow'):
            raise SnarfException, "Content-Type %s is not allowed" % type
    cleanurl = '%s://%s' % (parts[0], parts[1])
    if parts[2]:
        cleanurl = '%s%s' % (cleanurl, parts[2])
    if parts[3]:
        cleanurl = '%s;%s' % (cleanurl, parts[3])
    if parts[4]:
        cleanurl = '%s?%s' % (cleanurl, parts[4])
    return cleanurl

def handle_snarf(bot, ievent, direct=True):
    """ snarf provided url or last url in log """
    if not ievent.rest and (not urlcache.has_key(bot.name) or not \
urlcache[bot.name].has_key(ievent.printto)):
        ievent.missing('<url>')
        return
    elif not ievent.rest:
        url = urlcache[bot.name][ievent.printto]
    else:
        url = ievent.rest
    try:
        url = valid_url(url)
    except KeyError:
        ievent.reply("can't detect content type")
        return
    except SnarfException, e:
        if direct:
            ievent.reply('unable to snarf: %s' % str(e))
        return
    except urllib2.HTTPError, e:
        ievent.reply('unable to snarf: %s' % str(e))
        return
    except urllib2.URLError, ex:
        ievent.reply('unable to snarf: %s' % str(ex))
        return False
    if not url:
        ievent.reply('invalid url')
        return
    try:
        title = geturl_title(url)
    except socket.timeout:
        ievent.reply('%s socket timeout' % url)
        return
    except urllib2.HTTPError, e:
        ievent.reply('error: %s' % e)
        return
    if title:
        host = urlparse.urlparse(url)[1]
        if len(host) > 20:
            host = host[0:20] + '...'
        ievent.reply('%s: %s' % (host, title))
    else:
        ievent.reply('no title found at %s' % urlparse.urlparse(url)[1])

cmnds.add('snarf', handle_snarf, 'USER')
examples.add('snarf', 'fetch the title from an URL', \
'snarf http://gozerbot.org')
aliases.data['@'] = 'snarf'
aliases.data['title'] = 'snarf'

def handle_snarf_enable(bot, ievent):
    """ enable snarfing in channel """
    if not cfg.data.has_key(bot.name):
        cfg.data[bot.name] = {}
    cfg.data[bot.name][ievent.printto] = True
    cfg.save()
    ievent.reply('ok')

cmnds.add('snarf-enable', handle_snarf_enable, 'OPER')
examples.add('snarf-enable', 'enable snarfing in the channel', 'snarf-enable')
aliases.data['snarf-on'] = 'snarf-enable'

def handle_snarf_disable(bot, ievent):
    """ disable snarfing in channel """
    if not cfg.data.has_key(bot.name):
        ievent.reply('ok')
        return
    cfg.data[bot.name][ievent.printto] = False
    cfg.save()
    ievent.reply('ok')

cmnds.add('snarf-disable', handle_snarf_disable, 'OPER')
examples.add('snarf-disable', 'disable snarfing in the channel', \
'snarf-disable')
aliases.data['snarf-off'] = 'snarf-disable'

def handle_snarf_list(bot, ievent):
    """ show channels in which snarfing is enabled """
    snarfs = []
    names  = cfg.data.keys()
    names.sort()
    for name in names:
        targets = cfg.data[name].keys()
        targets.sort()
        snarfs.append('%s: %s' % (name, ' '.join(targets)))
    if not snarfs:
        ievent.reply('none')
    else:
        ievent.reply('snarfers enable on: %s' % ', '.join(snarfs))

cmnds.add('snarf-list', handle_snarf_list, 'OPER')
examples.add('snarf-list', 'show in which channels snarfing is enabled', \
'snarf-list')

def handle_validate(bot, ievent):
    """ validate provided url or last url in log """
    if not ievent.rest and not urlcache.has_key(bot.name) and not \
urlcache[bot.name].has_key(ievent.printto):
        ievent.missing('<url>')
        return
    elif not ievent.rest:
        url = urlcache[bot.name][ievent.printto]
    else:
        url = ievent.rest
    try:
        url = valid_url(url)
    except urllib2.HTTPError, e:
        ievent.reply('error: %s' % e)
        return
    if not url:
        ievent.reply('invalid or bad URL')
        return
    result = geturl_validate(url)
    if result:
        host = urlparse.urlparse(url)[1]
        if len(host) > 20:
            host = host[0:20] + '...'
        ievent.reply('%s: %s | modified: %s | server: %s | size: %s | \
content-type: %s | encoding: %s | doctype: %s' % \
            tuple([host] + [result[x] for x in ['result', 'modified', \
'server', 'size', 'content', 'encoding', 'doctype']]))

cmnds.add('validate', handle_validate, 'USER')
examples.add('validate', 'validate an URL', 'validate http://gozerbot.org')
aliases.data['valid'] = 'validate'


def privmsgpre(bot, ievent):
    test_url = re_url_match.search(ievent.txt)
    if test_url:
        return 1

def privmsgcb(bot, ievent):
    """ callback for urlcache """
    test_url = re_url_match.search(ievent.txt)
    url = test_url.group(1)
    if not urlcache.has_key(bot.name):
        urlcache[bot.name] = {}
    urlcache[bot.name][ievent.printto] = url
    rlog(0, 'snarf', 'cached url %s on %s (%s)' % (url, ievent.printto, \
bot.name))
    if cfg.data.has_key(bot.name) and cfg.data[bot.name]\
.has_key(ievent.printto) and cfg.data[bot.name][ievent.printto]:
        nevent = copy.copy(ievent)
        nevent.rest = url
        handle_snarf(bot, nevent, False)

callbacks.add('PRIVMSG', privmsgcb, privmsgpre, threaded=True)
jcallbacks.add('Message', privmsgcb, privmsgpre, threaded=True)
