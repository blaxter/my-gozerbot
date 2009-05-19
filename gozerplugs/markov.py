# plugs/markov.py
#
#

"""

Markov Talk for Gozerbot

The Chain:
    (predictate) -> [list of possible words]

TODO:
    - Propabilities
    - Start searching for full sentence, not just the first ORDER_K words 
      of a sentence
"""

__copyright__ = 'this file is in the public domain'
__author__ =  'Bas van Oostveen'
__coauthor__ = 'Bart Thate <bart@gozerbot.org>'
__gendocfirst__ = ['markov-enable', ]
__gendoclast__ = ['markov-disable', ]
__depend__ = ['log', ]

from gozerbot.datadir import datadir
from gozerbot.generic import rlog, geturl, striphtml, jsonstring
from gozerbot.persist.persist import PlugPersist
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.callbacks import callbacks, jcallbacks
from gozerbot.plughelp import plughelp
from gozerbot.plugins import plugins
from gozerbot.threads.thr import start_new_thread
from gozerbot.utils.statdict import Statdict
from gozerbot.utils.limlist import Limlist
from os.path import join as _j
import time, re, random, types

from gozerbot.persist.persistconfig import PersistConfig

plughelp.add('markov', 'Gozerbot speaking madness')

cfg = PersistConfig()
cfg.define('enable', [])
cfg.define('command', 1)
cfg.define('onjoin', [])

def enabled(botname, channel):
    if jsonstring([botname, channel]) in cfg['enable']:
        return True

# Markers (is Marker the correct name for this?)
class Marker: pass
class BeginMarker(Marker): pass
class EndMarker(Marker): pass
class NickMarker(Marker): pass

# Tokens
TOKEN = Marker()
TOKEN_BEGIN = BeginMarker()
TOKEN_END = EndMarker()
TOKEN_NICK = NickMarker()

# Order-k, use predictate [-k:] = [word,word,]
# if ORDER_K==1: { ('eggs'):['with','spam',], 'with': ['bacon','green',] }
# if ORDER_K==2: { ('eat','eggs'):['with',TOKEN,), ('eggs','with'): ['bacon',] }
# ...
# Logical setting is often 2 or 3
ORDER_K = 2

# Maximum generation cycles
MAXGEN = 500

markovlearn = PlugPersist('markovlearn', [])
markovwords = {}
markovwordi = []
markovchains = {}

cfg.define('loud', 1)

def init():
    """ init plugin """
    # check if enabled
    if not cfg.get('enable'):
        return 1
    # if so register callbacks
    callbacks.add("PRIVMSG", cb_markovtalk, cb_markovtalk_test, threaded=True)
    callbacks.add('JOIN', cb_markovjoin, threaded=True)
    jcallbacks.add('Message', cb_markovtalk, cb_jmarkovtalk_test, \
threaded=True)
    # learn log or url on startup
    start_new_thread(markovtrain, (markovlearn.data,))
    return 1

def size():
    """ return size of markov chains """
    return len(markovchains)

def markovtrain(l):
    """ train items in list """
    time.sleep(1)
    for i in l:
        if i.startswith('http://'):
            start_new_thread(markovlearnurl, (i,))
        else:
            start_new_thread(markovlearnlog, (i,))
    return 1
	
def iscommand(bot, ievent):
    """ check to see if ievent is a command """
    if not ievent.txt:
        return 0
    try:
        cc = bot.channels[ievent.channel]['cc']
    except (TypeError, KeyError):
        cc = None
    txt = ""
    if cc and ievent.txt[0] == cc:
        txt = ievent.txt[1:]
    if ievent.txt.startswith(bot.nick + ':') or \
ievent.txt.startswith(bot.nick + ','):
        txt = ievent.txt[len(bot.nick)+1:]
    oldtxt = ievent.txt
    ievent.txt = txt
    result = plugins.woulddispatch(bot, ievent)
    ievent.txt = oldtxt
    return result

def cb_markovjoin(bot, ievent):
    """ callback to run on JOIN """
    # check if its we who are joining
    nick = ievent.nick.lower()
    if nick in bot.splitted:
        return
    if nick == bot.nick.lower():
        return
    # check if (bot.name, ievent.channel) is in onjoin list if so respond
    try:
        onjoin = cfg.get('onjoin')
    except KeyError:
        onjoin = None
    if type(onjoin) != types.ListType:
        return
    if jsonstring([bot.name, ievent.channel]) in onjoin:
        txt = getreply(bot, ievent, ievent.nick + ':')
        if txt:
            ievent.reply('%s: %s' % (ievent.nick, txt))
            
def cb_markovtalk_test(bot, ievent):
    """ callback precondition """
    if not ievent.usercmnd:
        return 1

def cb_jmarkovtalk_test(bot, ievent):
    """ callback precondition """
    if not ievent.usercmnd:
        return 1

def cb_markovtalk(bot, ievent):
    """ learn from everything that is being spoken to the bot """
    # check for relay
    if ievent.txt.count('[%s]' % bot.nick) > 0:
        return
    # strip
    txt = strip_txt(bot, ievent.txt)
    # markovtalk_learn
    if enabled(bot.name, ievent.channel):
        markovtalk_learn(txt)
    # if command is set in config then we don't respond in callback
    elif not cfg.get('loud'):
        return 
    itxt = ievent.txt.lower()
    # check is bot.nick is in ievent.txt if so give response
    botnick = bot.nick.lower()
    #responsenicks = (botnick, botnick+":", botnick+",")
    if botnick in ievent.txt or cfg.get('loud') and ievent.msg: 
        # reply when called 
        result = getreply(bot, ievent, txt)
	# dont reply if answer is going to be the same as question
        if not result:
            return
        if result.lower() == txt.lower():
            return
        ievent.reply(result)

# re to strip first word of logline
txtre = re.compile('^\S+ ')

def markovlearnlog(chan):
    """ learn a log """
    from gozerplugs.log import logs    
    logmap = logs.getmmap(chan)
    if not logmap:
        rlog(10, 'markov', "can't get logfile of %s" % chan)
        return
    # process lines in mmaped file
    lines = 0
    rlog(10, 'markov', 'learning %s log' % chan)
    while 1:
        if lines % 10 == 0:
            time.sleep(0.001)
        line = logmap.readline()
        if not line:
            break
        try:
            items = line.strip().split(',', 4)
            if items[3] == 'bot@bot':
                continue
            if items[4].startswith('CMND:'):
                continue
        except:
            continue
        try:
            txt = re.sub(txtre, '', items[4])
            markovtalk_learn(txt + '\n')
        except IndexError:
            continue
        lines += 1
    logmap.close()
    rlog(10, 'markov', 'learning %s log done' % chan)
    return lines

def markovlearnurl(url):
    """ learn an url """
    lines = 0
    rlog(10, 'markov', 'learning %s' % url)
    try:
        f = geturl(url)
        for line in f.split('\n'):
            line = striphtml(line)
            if lines % 10 == 0:
                time.sleep(0.01)
            line = line.strip()
            if not line:
                continue
            markovtalk_learn(line)
            lines += 1
    except Exception, e:
        rlog(10, 'markov', str(e))
    rlog(10, 'markov', 'learning %s done' % url)
    return lines

def strip_txt(bot, txt):
    """ strip bot nick and addressing """
    # TODO: strip other nicks, preferably replacing them with something like 
    # TOKEN_NICK
    txt = txt.replace("%s," % bot.nick, "")
    txt = txt.replace("%s:" % bot.nick, "")
    txt = txt.replace("%s" % bot.nick, "")
    return txt.strip()

def msg_to_array(msg):
    """ convert string to lowercased items in list """
    return [word.strip().lower() for word in msg.strip().split()]

def mw(w):
    if not w in markovwords:
        wi = len(markovwordi)
        markovwordi.append(w)
        markovwords[w] = wi
        return wi
    return markovwords[w]

def o2i(order):
    return tuple(mw(w) for w in order)

def i2o(iorder):
    return tuple(markovwordi[i] for i in iorder)

def markovtalk_learn(text_line):
    """ this is the function were a text line gets learned """
    text_line = msg_to_array(text_line)
    length = len(text_line)
    order = [TOKEN, ] * ORDER_K
    for i in range(length-1):
        order.insert(0, text_line[i])
        order = order[:ORDER_K]
        next_word = text_line[i+1]
        key = markovchains.setdefault(o2i(order), [])
        if not next_word in key:
            key.append(mw(next_word))

def getreply(bot, ievent, text_line):
    """ get 20 replies and choose the largest one """
    if not text_line:
        return ""
    text_line = msg_to_array(text_line)
    wordsizes = {}
    maxsize = 0
    for i in text_line:
        wordsizes[len(i)] = i
        if len(i) > maxsize:
            maxsize = len(i)
    results = []
    keywords = ['is', ]
    max = maxsize
    for i in range(7):
        p = ['', ]
        try:
            p[0] = wordsizes[max]
        except KeyError:
            p[0] = random.choice(text_line)
        if len(p) > 2:
            p.append(random.choice(text_line))
        #random.shuffle(p)
        if len(p) < 2:
            p.append('is')
        line = getline(' '.join(p))
        if line and line not in results:
            results.append(line)
        else:
            max -= 1
            if max < 1:
                max = maxsize
    if not results:
        return ""
    #highest = []
    #high = 0
    #for i in results:
    #    if len(i) > high:
    #        highest.insert(0, i)
    #        high = len(i)
    #for i in results:
    #    if wordsizes[maxsize] in i:
    #            return i
    #res = random.choice(highest)
    res = []
    for result in results[:4]:
        if len(result.split()) > 1:
            res.append(result.capitalize())
    return '. '.join(res)

def getline(text_line):
    """ get line from markovvhains """
    text_line = msg_to_array(text_line)
    order = Limlist(ORDER_K)
    for i in range(ORDER_K):
        order.append(TOKEN)
    teller = 0
    for i in text_line[:ORDER_K-1]:
        order[teller] = i
        teller += 1
    output = ""
    for i in range(MAXGEN):
        try:
            successorList = i2o(markovchains[o2i(order)])
        except KeyError:
            continue
        #print successorList
        keyword = successorList[0]
        word = random.choice(successorList)
        if not word:
            break
        if word not in output:
            output = output + " "  + word
        order.insert(0, word)
        order = order[:ORDER_K]
    return output.strip()
    
def handle_markovsize(bot, ievent):
    """ markov-size .. returns size of markovchains """
    ievent.reply("I know %s phrases" % str(len(markovchains.keys())))

cmnds.add('markov-size', handle_markovsize, 'OPER')
examples.add('markov-size', 'size of markovchains', 'markov-size')

def handle_markovlearn(bot, ievent):
    """ command to let the bot learn a log or an url .. learned data 
        is not persisted """
    try:
        item = ievent.args[0]
    except IndexError:
        ievent.reply('<channel>|<url>')
        return
    if item.startswith('http://'):
        nrlines = markovlearnurl(item)
        ievent.reply('learned %s lines' % nrlines)
        return
    from gozerplugs.log import logs
    if item in logs.loglist:
        ievent.reply('learning log file %s' % item)
        nrlines = markovlearnlog(item)
        ievent.reply('learned %s lines' % nrlines)
        return
    else:
        ievent.reply('logging is not enabled in %s' % item)

cmnds.add('markov-learn', handle_markovlearn, 'OPER')
examples.add('markov-learn', 'learn a logfile or learn an url', \
'1) markov-learn #dunkbots 2) markov-learn http://gozerbot.org')
 
def handle_markovlearnadd(bot, ievent):
    """ add log or url to be learned at startup or reload """
    try:
        item = ievent.args[0]
    except IndexError:
        ievent.missing('<channel>|<url>')
        return
    if item in markovlearn.data:
        ievent.reply('%s is already in learnlist' % item)
        return
    markovlearn.data.append(item)
    markovlearn.save()
    handle_markovlearn(bot, ievent)
    ievent.reply('done')

cmnds.add('markov-learnadd', handle_markovlearnadd, 'OPER')
examples.add('markov-learnadd', 'add channel or url to permanent learning .. \
this will learn the item on startup', '1) markov-learnadd #dunkbots 2) \
markov-learnadd http://gozerbot.org')

def handle_markovlearnlist(bot, ievent):
    """ show the learnlist """
    ievent.reply(str(markovlearn.data))

cmnds.add('markov-learnlist', handle_markovlearnlist, 'OPER')
examples.add('markov-learnlist', 'show items in learnlist', \
'markov-learnlist')

def handle_markovlearndel(bot, ievent):
    """ remove item from learnlist """
    try:
        item = ievent.args[0]
    except IndexError:
        ievent.missing('<channel>|<url>')
        return
    if item not in markovlearn.data:
        ievent.reply('%s is not in learnlist' % item)
        return
    markovlearn.data.remove(item)
    markovlearn.save()
    ievent.reply('done')

cmnds.add('markov-learndel', handle_markovlearndel, 'OPER')
examples.add('markov-learndel', 'remove item from learnlist', \
'1) markov-learndel #dunkbots 2) markov-learndel http://gozerbot.org')

def handle_markov(bot, ievent):
    """ this is the command to make the bot reply a markov response """
    if not enabled(bot.name, ievent.channel):
        ievent.reply('markov is not enabled in %s' % ievent.channel)
        return
    if not ievent.rest:
        ievent.missing('<txt>')
        return
    result = getreply(bot, ievent, strip_txt(bot, ievent.rest))
    if result:
        ievent.reply(result)

cmnds.add('markov', handle_markov, ['USER', 'WEB', 'CLOUD'])
examples.add('markov', 'ask for markov response', 'markov nice weather')

def handle_markovonjoinadd(bot, ievent):
    """ add channel to onjoin list """
    try:
        channel = ievent.args[0]
    except IndexError:
        channel = ievent.channel
    if (bot.name, channel) in cfg.get('onjoin'):
        ievent.reply('%s already in onjoin list' % channel)
        return
    cfg.get('onjoin').append((bot.name, channel))
    cfg.save()
    ievent.reply('%s added' % channel)

cmnds.add('markov-onjoinadd', handle_markovonjoinadd, 'OPER')
examples.add('markov-onjoinadd', 'add channel to onjoin config', \
'1) markov-onjoinadd 2) markov-onjoinadd #dunkbots')

def handle_markovonjoinremove(bot, ievent):
    """ remove channel from onjoin list """
    try:
        channel = ievent.args[0]
    except IndexError:
        channel = ievent.channel
    try:
        cfg.get('onjoin').remove((bot.name, channel))
    except ValueError:
        ievent.reply("%s not in onjoin list" % channel)
        return
    cfg.save()
    ievent.reply('%s removed' % channel)

cmnds.add('markov-onjoinremove', handle_markovonjoinremove, 'OPER')
examples.add('markov-onjoinremove', 'remove channel from onjoin config', \
'1) markov-onjoinremove 2) markov-onjoinremove #dunkbots')

def handle_markovenable(bot, ievent):
    """ enable markov in a channel .. learn the log of that channel """
    try:
        channel = ievent.args[0]
    except IndexError:
        channel = ievent.channel
    if not enabled(bot.name, channel):
        cfg.get('enable').append(jsonstring([bot.name, channel]))
    else:
        ievent.reply('%s is already enabled' % channel)
        return
    cfg.save()
    markovlearn.data.append(channel)
    markovlearn.save()
    plugins.reload('gozerplugs', 'markov')
    ievent.reply('%s enabled' % channel)

cmnds.add('markov-enable', handle_markovenable, 'OPER')
examples.add('markov-enable', 'enable markov learning in [<channel>]', '1) \
markov-enable 2) markov-enable #dunkbots')

def handle_markovdisable(bot, ievent):
    """ disable markov in a channel """
    try:
        channel = ievent.args[0]
    except IndexError:
        channel = ievent.channel
    if enabled(bot.name, channel):
        cfg.get('enable').remove(jsonstring([bot.name, channel]))
    else:
        ievent.reply('%s is not enabled' % channel)
        return
    cfg.save()
    try:
        markovlearn.data.remove(channel)
        markovlearn.save()
    except ValueError:
        pass
    plugins.reload('gozerplugs', 'markov')
    ievent.reply('%s disabled' % channel)

cmnds.add('markov-disable', handle_markovdisable, 'OPER')
examples.add('markov-disable', 'disable markov learning in [<channel>]', '1) \
markov-disable 2) markov-disable #dunkbots')
