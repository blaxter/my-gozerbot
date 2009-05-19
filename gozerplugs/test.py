# gozerplugs/test.py
#
#

from gozerbot.utils.exception import exceptionmsg
from gozerbot.tests import tests
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.irc.ircevent import Ircevent
from gozerbot.users import users
from gozerbot.plughelp import plughelp
from gozerbot.partyline import partyline

plughelp.add('test', 'plugin to do tests')

import time, random

donot = ['quit', 'reboot', 'shutdown', 'exit', 'delete', 'halt', 'upgrade', \
'install', 'reconnect', 'wiki', 'weather', 'sc', 'jump', 'disable', 'dict', \
'snarf', 'validate', 'popcon']

def dummy(a, b=None):
    return ""

import gozerbot.utils.url
import gozerbot.generic
oldgeturl = gozerbot.utils.url.geturl
oldgeturl2 = gozerbot.utils.url.geturl2 

def handle_testplugs(bot, msg):
    if not ievent.isdcc:
        ievent.reply('use this command in a /dcc chat with the bot')
        return
    gozerbot.utils.url.geturl = dummy
    gozerbot.utils.url.geturl2 = dummy
    gozerbot.generic.geturl = dummy
    gozerbot.generic.geturl2 = dummy
    if msg.rest:
        match = msg.rest
    else:
        match = ""
    try:
        users.add('test', ['test@test',], ['USER', 'OPER'])
    except Exception, ex:
        pass
    bot.channels.setdefault('test', {})
    try:
        loop = int(msg.options['--loop'])
    except (KeyError, ValueError):
        loop = 1
    for i in range(loop):
        msg.reply('starting loop %s' % str(i))
        examplez = examples.getexamples()
        random.shuffle(examplez)
        for example in examplez:
            if match and match not in example:
                continue
            skip = False
            for dont in donot:
                if dont in example:
                    skip = True
            if skip:
                continue
            if bot.jabber:
                from gozerbot.jabber.jabbermsg import Jabbermsg
                newmessage = Jabbermsg(msg.orig)
                newmessage.copyin(msg)
                newmessage.txt = '!' + example
                msg.reply('command: ' + example)  
                bot.domsg(newmessage)
            else:
                newmessage = Ircevent(msg.orig)
                newmessage.copyin(msg)
                newmessage.txt = '!' + example
                msg.reply('command: ' + example)  
                bot.domsg(newmessage)
            try:
                time.sleep(int(msg.options['--sleep']))
            except (KeyError, ValueError):
                pass
    gozerbot.utils.url.geturl = oldgeturl
    gozerbot.utils.url.geturl2 = oldgeturl2
    gozerbot.generic.geturl = oldgeturl
    gozerbot.generic.geturl2 = oldgeturl2

cmnds.add('test-plugs', handle_testplugs, ['OPER', ], options={'--sleep': '1', '--loop': '1'}, threaded=True)

def handle_testsrun(bot, ievent):
    if not ievent.isdcc:
        ievent.reply('use this command in a /dcc chat with the bot')
        return
    errors = []
    toolate = []
    err = {}
    try:
        loop = ievent.options['--loop']
        loop = int(loop)
    except (KeyError, ValueError):
        loop = 1
    teller = 0
    for nr in range(loop):
        for i in range(len(tests.tests)):
            test = tests.tests[i]
            if ievent.rest and ievent.rest not in test.plugin:
                continue
            if test.expect:
                teller += 1
            try:
                starttime = time.time()
                result = test.run(bot, ievent)
                finished = time.time()
                if finished - starttime > 5:
                    toolate.append(test.execstring)
                if not result:
                    continue
                if not result.error:
                    ievent.reply("OK %s ==> %s" % (test.execstring, test.response))
                else:
                    errors.append(test)
                    ievent.reply('ERROR %s (%s): %s ==> %s (%s)' % (test.error, test.where, test.execstring, test.response, test.expect))
            except Exception, ex:
                errors.append(test)
                test.error = exceptionmsg()
                err[test.execstring] = test.error
                ievent.reply(test.error)
        ievent.reply('%s tests run .. %s errors' % (teller, len(errors)))
    if err:
        ievent.reply('errors: ', err)
    if toolate:
        ievent.reply('toolate: ', toolate, dot=True)

cmnds.add('test-run', handle_testsrun, 'OPER', threaded=True, options={'--loop': '1'})
examples.add('test-run', 'run the tests', 'test-run')

def handle_forcedreconnect(bot, ievent):
    if bot.jabber:
        bot.disconnectHandler()
    else:
        bot.sock.close()

cmnds.add('test-forcedreconnect', handle_forcedreconnect, 'OPER')
