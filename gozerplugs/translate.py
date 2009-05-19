# Description: freetranslation.com parser
# Author: Wijnand 'tehmaze' Modderman - http://tehmaze.com
# License: BSD
# License: For non-commercial use only: http://www.freetranslation.com/terms.htm

import httplib
import re
import types
import urllib
import urlparse
from gozerbot.commands import cmnds
from gozerbot.config import config
from gozerbot.examples import examples
from gozerbot.generic import geturl, posturl, waitforqueue
from gozerbot.plughelp import plughelp
# compatibility check (since r1701)
try:
    from gozerbot.textutils import html_unescape
except ImportError:
    import htmllib

    def html_unescape(s):
        p = htmllib.HTMLParser(None)
        p.save_bgn()
        p.feed(s)
        return p.save_end()

plughelp.add('translate', 'translate between languages')

class TranslateLanguageException(Exception):
    pass

class TranslateLoginException(Exception):
    pass

class Translate:
    
    lang = ['English/Spanish', 'English/French', 'English/German', 'English/Italian', 'English/Dutch', 'English/Portuguese', 'English/Russian', 'English/Norwegian', 'English/SimplifiedChinese', 'English/TraditionalChinese', 'English/Japanese', 'Spanish/English', 'French/English', 'German/English', 'Italian/English', 'Dutch/English', 'Portuguese/English', 'Russian/English', 'Japanese/English']
    re_username = re.compile('<input type="hidden" name="username" value="([^"]+)" />', re.I | re.M)
    re_password = re.compile('<input type="hidden" name="password" value="([^"]+)" />', re.I | re.M)
    
    def translate(self, lang_from, lang_to, text):
        # fix case stuff
        lang_from = lang_from.title().replace('chinese', 'Chinese')
        lang_to   = lang_to.title().replace('chinese', 'Chinese')
        if lang_from == 'Chinese':
            lang_from = 'SimplifiedChinese'
        if lang_to == 'Chinese':
            lang_to = 'SimplifiedChinese'
        lang = '%s/%s' % (lang_from, lang_to)
        if not lang in self.lang:
            raise TranslateLanguageException('no such language combination')
        else:
            # oh, this is not needed, ah well, in case we'll ever need it .. ;-)
            #credentials = self.fetch_credentials()
            #if not credentials:
            #    raise TranslateLoginException('Could not fetch username and password')
            #return self.translate_web(credentials, lang, text)
            return self.translate_web({}, lang, text)

    def fetch_credentials(self):
        """On the front page, a username and password are generated and have a limited validity."""
        html = geturl('http://www.freetranslation.com')
        test_username = self.re_username.search(html)
        test_password = self.re_password.search(html)
        credentials = {}
        if test_username and test_password:
            credentials['username'] = test_username.group(1)
            credentials['password'] = test_password.group(1)
        return credentials

    def translate_web(self, postdata, lang, text):
        # defaults
        postdata.update({'language': lang, 'sequence': 'core', 'mode': 'html',
            'template': 'results_en-us.htm', 'charset': 'UTF-8', 'a': 'a',
            'e': 'e', 'i': 'i', 'o': 'o', 'u': 'u', 'misc': 'misc', 
            'Submit': 'FREE Translation'})
        # text
        postdata.update({'srctext': text})
        # pick correct server
        server = 'ets.freetranslation.com'
        if 'chinese' in lang.lower() or 'russian' in lang.lower():
            server = 'ets6.freetranslation.com'
        elif 'japanese' in lang.lower():
            server = 'tets9.freetranslation.com'
        result = posturl('http://%s/' % server, {}, postdata)
        for line in result.read().splitlines():
            # <textarea name="dsttext" cols="40" rows="6">ff test or works this</textarea><br />
            if 'name="dsttext"' in line:
                return line.split('>')[1].split('</textarea')[0]
        return None

translate = Translate()

def handle_translate(bot, ievent):
    if ievent.inqueue:
        text = ' '.join(waitforqueue(ievent.inqueue, 5))
    elif len(ievent.args) < 3:
        ievent.missing('<from language> <to language> <text>')
        return
    else:
        text = ' '.join(ievent.args[2:])
    try:
        result = translate.translate(ievent.args[0], ievent.args[1], text)
        if result:
            ievent.reply(html_unescape(result))
        else:
            ievent.reply('translation failed (no result)')
    except TranslateLanguageException, e:
        ievent.reply(str(e))

cmnds.add('translate', handle_translate, 'USER')
examples.add('translate', 'translate between languages', 'translate English Dutch how do you do')

def handle_translate_langs(bot, ievent):
    langs = []
    for lang in translate.lang:
        lang = lang.split('/')
        for l in lang:
            if not l in langs:
                langs.append(l)
    langs.sort()
    ievent.reply('available languages: %s' % ', '.join(langs))

cmnds.add('translate-lang', handle_translate_langs, 'USER')

trmap = {
    'de': 'German',
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'it': 'Italian',
    'ja': 'Japanese',
    'jp': 'Japanese',
    'nl': 'Dutch',
    'no': 'Norwegian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'cn': 'SimplifiedChinese'
    }
re_tr = re.compile('^(\S\S)[>\s](\S\S)')

def handle_tr(bot, ievent):
    if not re_tr.match(ievent.txt.strip()):
        return ievent.missing('<from lang>to lang> <text>')
    else:
        if ievent.inqueue:
            text = ' '.join(waitforqueue(ievent.inqueue, 5))
        elif '>' in ievent.args[0]:
            text = ' '.join(ievent.args[1:])
        else:
            text = ' '.join(ievent.args[2:])
        test_tr = re_tr.search(ievent.args[0])
        if not test_tr or not trmap.has_key(test_tr.group(1).lower()) or \
             not trmap.has_key(test_tr.group(2).lower()):
            langs = trmap.keys()
            langs.sort()
            return ievent.reply('invalid language combination, available languages are: %s' % ', '.join(langs))
        lang1 = trmap[test_tr.group(1).lower()]
        lang2 = trmap[test_tr.group(2).lower()]
        try:
            result = translate.translate(lang1, lang2, text)
            if result:
                ievent.reply(html_unescape(result))
            else:
                ievent.reply('translation failed (no result)')
        except TranslateLanguageException, e:
            ievent.reply(str(e))

cmnds.add('tr', handle_tr, 'USER')
examples.add('tr', 'translate between two languages', 'tr nl>en het is mooi weer vandaag')
