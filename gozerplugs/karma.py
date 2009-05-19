# plugs/karma.py
#
#

""" karma plugin """

__copyright__ = 'this file is in the public domain'
__depending__ = ['fans', 'quote']

from gozerbot.tests import tests
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.redispatcher import rebefore
from gozerbot.datadir import datadir
from gozerbot.generic import handle_exception, rlog, lockdec
from gozerbot.utils.statdict import Statdict
from gozerbot.aliases import aliases
from gozerbot.plughelp import plughelp
from gozerbot.config import config
import thread, pickle, time, os

from gozerbot.database.alchemy import Base, create_session, trans
from datetime import datetime
from time import localtime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Sequence
import sqlalchemy as sa

class Karma(Base):
    __tablename__ = 'karma'
    __table_args__ = {'useexisting': True}
    item = Column('item', String(255), primary_key=True)
    value = Column('value', Integer, nullable=False)

    def __init__(self, item, value):
        self.item = item
        self.value = value

class WhyKarma(Base):
    __tablename__ = 'whykarma'
    __table_args__ = {'useexisting': True}
    item = Column('item', String(255), nullable=False)
    updown = Column('updown', String(10), nullable=False)
    why = Column('why', Text, nullable=False)
    __mapper_args__ = {'primary_key':[item,updown,why]}

    def __init__(self, item, updown, why):
        self.item = item
        self.updown = updown
        self.why = why

class WhoKarma(Base):
    __tablename__ = 'whokarma'
    __table_args__ = {'useexisting': True}
    item = Column('item', String(255), nullable=False)
    nick = Column('nick', String(255), nullable=False)
    updown = Column('updown', String(10), nullable=False)
    __mapper_args__ = {'primary_key':[item,nick,updown]}

    def __init__(self, item, nick, updown):
        self.item = item
        self.nick = nick
        self.updown = updown

## UPGRADE PART

def upgrade():
    teller = 0
    oldfile = datadir + os.sep + 'old'
    dbdir = datadir + os.sep + 'db' + os.sep + 'karma.db'
    if os.path.exists(dbdir):
        try:
            from gozerbot.database.db import Db
            db = Db(dbtype='sqlite')
            db.connect('db/karma.db')
            result = db.execute(""" SELECT * FROM karma """)
            if result:
                for i in result:
                    try:
                        karma.add(i[0], i[1])
                    except sa.exc.IntegrityError:
                        pass
                    teller += 1
            result = db.execute(""" SELECT * FROM whokarma """)
            if result:
                for i in result:
                    if i[2] == 'up':
                        karma.setwhoup(i[0], i[1])
                    else:
                        karma.setwhodown(i[0], i[1])
            result = db.execute(""" SELECT * FROM whykarma """)
            if result:
                for i in result:
                    karma.addwhy(*i)
        except Exception, ex:
            handle_exception()
        return teller
    try:
        from gozerbot.utils.generic import dosed
        from gozerbot.database.db import Db
        from gozerbot.compat.karma import Karma
        #dosed(oldfile, 's/cgozerbot\.compat/cgozerplugs/')
        oldkarma = Karma(oldfile) 
        if not oldkarma:
            return
        k = oldkarma
        for i,j in k.karma.iteritems():
            karma.add(i,j)
            teller += 1
        for i,j in k.reasonup.iteritems():
            for z in j:
                karma.addwhy(i, 'up', z)

        for i,j in k.reasondown.iteritems():
            for z in j:
                karma.addwhy(i, 'up', z)

        for i,j in k.whodown.iteritems():
            for z in j:
                karma.setwhodown(i, z)

        for i,j in k.whoup.iteritems():
            for z in j:
                karma.setwhoup(i, z)
    except Exception, ex:
        rlog(10, 'karma', 'failed to upgrade: %s' % str(ex))
        return
    rlog(10, 'karma', 'upgraded %s karma items' % str(teller))

# END UPGRADE PART

plughelp.add('karma', 'maintain karma of items .. use ++ to raise karma by 1 \
or use -- to lower by 1 .. reason might be given after a "#"')

class KarmaDb(object):

    """ karma object """

    def save(self):
        pass

    def size(self):
        """ return number of items """
        s = create_session()
        count = s.query(sa.func.count(Karma.item)).first()[0]
        return count

    @trans
    def add(self, session, item, value):
        item = item.lower()
        karma = Karma(item, value)
        session.add(karma)
        session.commit()
        rlog(10, 'karma', 'added %s: %s' % (item, value))
        return 1

    def get(self, item):
        """ get karma of item """
        item = item.lower()
        s = create_session()
        karma = s.query(Karma).filter(Karma.item==item).first()
        if karma:
            return karma.value

    @trans
    def delete(self, session, item):
        """ delete karma item """
        item = item.lower()
        karma = session.query(Karma).filter(Karma.item==item).first()
        if karma:
            session.delete(karma)
            return 1

    @trans
    def addwhy(self, session, item, updown, reason):
        """ add why of karma up/down """
        item = item.lower()
        whykarma = WhyKarma(item, updown, reason)
        session.save(whykarma)

    @trans
    def upitem(self, session, item, reason=None):
        """ up a karma item with/without reason """
        item = item.lower()
        karma = session.query(Karma).filter(Karma.item==item).first()
        if not karma:
            karma = Karma(item, 0)
            session.add(karma)
        karma.value = karma.value + 1
        if reason:
            whykarma = WhyKarma(item, 'up', reason.strip())
            session.save(whykarma)

    @trans
    def down(self, session, item, reason=None):
        """ lower a karma item with/without reason """
        item = item.lower()
        s = create_session()
        karma = s.query(Karma).filter(Karma.item==item).first()
        if not karma:
            karma = Karma(item, 0)
            session.add(karma)
        karma.value = karma.value - 1
        if reason:
            whykarma = WhyKarma(item, 'down', reason.strip())
            session.save(whykarma)

    def whykarmaup(self, item):
        """ get why of karma ups """
        s = create_session()
        item = item.lower()
        karma = s.query(WhyKarma).filter(WhyKarma.item==item).filter(WhyKarma.updown=='up')
        if karma:
            return [k.why for k in karma]

    def whykarmadown(self, item):
        """ get why of karma downs """
        s = create_session()
        item = item.lower()
        karma = s.query(WhyKarma).filter(WhyKarma.item==item).filter(WhyKarma.updown=='down')
        if karma:
            return [k.why for k in karma]

    @trans
    def setwhoup(self, session, item, nick):
        """ set who upped a karma item """
        item = item.lower()
        nick = nick.lower()
        whokarma = WhoKarma(item, nick, 'up')
        session.add(whokarma)
 
    @trans
    def setwhodown(self, session, item, nick):
        """ set who lowered a karma item """
        item = item.lower()
        nick = nick.lower()
        whokarma = WhoKarma(item, nick, 'down')
        session.add(whokarma)

    def getwhoup(self, item):
        """ get list of who upped a karma item """
        item = item.lower()
        s = create_session()
        karma = s.query(WhoKarma).filter(WhoKarma.item==item).filter(WhoKarma.updown=='up')
        if karma:
            return [k.nick for k in karma]

    def getwhodown(self, item):
        """ get list of who downed a karma item """
        item = item.lower()
        s = create_session()
        karma = s.query(WhoKarma).filter(WhoKarma.item==item).filter(WhoKarma.updown=='down')
        if karma:
            return [k.nick for k in karma]

    def search(self, item):
        """ search for matching karma item """
        item = item.lower()
        s = create_session()
        karma = s.query(Karma).filter(Karma.item.like('%%%s%%' % item))
        if karma:
            return karma

    def good(self, limit=10):
        """ show top 10 of karma items """
        statdict = Statdict()
        s = create_session()
        karma = s.query(Karma).all()
        if not karma:
            return []
        for i in karma:
            if i.item.startswith('quote '):
                continue
            statdict.upitem(i.item, i.value)
        return statdict.top(limit=limit)

    def bad(self, limit=10):
        """ show lowest 10 of negative karma items """
        statdict = Statdict()
        s = create_session()
        karma = s.query(Karma).all()
        if not karma:
            return []
        for i in karma:
            if i.item.startswith('quote '):
                continue
            statdict.upitem(i.item, i.value)
        return statdict.down(limit=limit)

    def quotegood(self, limit=10):
        """ show top 10 of karma items """
        statdict = Statdict()
        s = create_session()
        karma = s.query(Karma).all()
        if not karma:
            return []
        for i in karma:
            if not i.item.startswith('quote '):
                continue
            statdict.upitem(i.item, i.value)
        return statdict.top(limit=limit)

    def quotebad(self, limit=10):
        """ show lowest 10 of negative karma items """
        statdict = Statdict()
        s = create_session()
        karma = s.query(Karma).all()
        if not karma:
            return []
        for i in karma:
            if not i.item.startswith('quote '):
                continue
            statdict.upitem(i.item, i.value)
        return statdict.down(limit=limit)

    def whatup(self, nick):
        """ show what items are upped by nick """
        nick = nick.lower()
        statdict = Statdict()
        s = create_session()
        whokarma = s.query(WhoKarma).filter(WhoKarma.nick==nick).filter(WhoKarma.updown=='up')
        if not whokarma:
            return []
        for i in whokarma:
            statdict.upitem(i.item)
        return statdict.top()

    def whatdown(self, nick):
        """ show what items are upped by nick """
        nick = nick.lower()
        statdict = Statdict()
        s = create_session()
        whokarma = s.query(WhoKarma).filter(WhoKarma.nick==nick).filter(WhoKarma.updown=='down')
        if not whokarma:
            return []
        for i in whokarma:
            statdict.upitem(i.item)
        return statdict.top()

karma = KarmaDb()
Base.metadata.create_all()
assert(karma)

ratelimited = []
limiterlock = thread.allocate_lock()
limlock = lockdec(limiterlock)
nolimiter = False

def size():
    """ return number of kamra items """
    return karma.size()

def search(what, queue):
    rlog(10, 'karma', 'searched for %s' % what)
    result = karma.search(what)
    for i in result:
        queue.put_nowait("%s has karma %s" % (i[0], i[1]))

@limlock
def ratelimit(bot, ievent):
    """ karma rate limiter """
    if nolimiter:
        return 1
    waittime = 30
    limit = 2
    try:
        name = ievent.userhost
        # Create a state for this user and his/her karma-state if necessary
        if not bot.state.has_key(name):
            bot.state[name] = {}
        if not bot.state[name].has_key('karma'):
            bot.state[name]['karma'] = {'count': 0, 'time': time.time() } 
        # If the waittime has elapsed, reset the counter
        if time.time() > (bot.state[name]['karma']['time'] + waittime):
            bot.state[name]['karma']['count'] = 0 
        # Update counter
        bot.state[name]['karma']['count'] += 1
        # If counter is too high, limit :)
        if bot.state[name]['karma']['count'] > limit:
            if name in ratelimited:
                return 0
            ievent.reply("karma limit reached, you'll have to wait %s \
seconds" % int((bot.state[name]['karma']['time'] + waittime) - time.time()))
            ratelimited.append(name)
            return 0
        # Update time
        bot.state[name]['karma']['time'] = time.time()
        # Ratelimiting passed :)
        try:
            ratelimited.remove(name)
        except ValueError:
            pass
        return 1
    except Exception, ex:
        handle_exception(ievent)

def handle_karmaupgrade(bot, ievent):
    if karma.size():
         if '-f' in ievent.optionset:
             pass
         else:
             ievent.reply('there are already karma items in the main database .. not upgrading')
             ievent.reply('use the -f option to force an upgrade')
             return
    ievent.reply('upgrading karma items')
    nritems = upgrade()
    ievent.reply('%s items upgraded' % nritems)

cmnds.add('karma-upgrade', handle_karmaupgrade, 'OPER', options={'-f': ''})

def handle_karmaget(bot, ievent):
    """ karma-get <item> .. show karma of item """
    if not ievent.rest:
        ievent.missing('<item>')
        return
    else:
        item = ievent.rest
    result = karma.get(item)
    if result:
        ievent.reply("%s has karma %s" % (item, str(result)))
    else:
        ievent.reply("%s has no karma yet" % item)

cmnds.add('karma-get', handle_karmaget, ['USER', 'WEB', 'ANONKARMA', 'CLOUD'])
examples.add('karma-get', 'karma-get <item> .. show karma of <item>', \
'karma-get dunker')
aliases.data['karma'] = 'karma-get'

def nolimit():
    global nolimiter
    nolimiter = True

tests.start(nolimit).add('gozerbot++').add('karma-get gozerbot', 'gozerbot has karma (\d+)')

def handle_karmadel(bot, ievent):
    """ karma-del <item> .. delete karma item """
    if not ievent.rest:
        ievent.missing('<item>')
        return
    item = ievent.rest
    result = karma.delete(item)
    if result:
        ievent.reply("%s deleted" % item)
    else:
        ievent.reply("can't delete %s" % item)

cmnds.add('karma-del', handle_karmadel, ['OPER'])
examples.add('karma-del', 'karma-del <item> .. delete karma item', \
'karma-del dunker')
tests.add('boozer--').add('karma-del boozer', 'boozer deleted')

def handle_karmaup(bot, ievent):
    """ <item>++ ['#' <reason>] .. increase karma of item with optional \
        reason """
    if not ratelimit(bot, ievent):
        return
    (item, reason) = ievent.groups
    item = item.strip().lower()
    if not item:
        return
    karma.upitem(item, reason=reason)
    karma.setwhoup(item, ievent.nick)
    ievent.reply('karma of '+ item + ' is now ' + str(karma.get(item)))

rebefore.add(8, '^(.+)\+\+\s+#(.*)$', handle_karmaup, ['USER', 'KARMA', \
'ANONKARMA'],  allowqueue=False)
examples.add('++', "<item>++ ['#' <reason>] .. higher karma of item with 1 \
(use optional reason)", '1) gozerbot++ 2) gozerbot++ # top bot')
tests.add('gozerbot++', 'karma of gozerbot is now (\d+)')
tests.add('gozerbot++ # top bot', 'karma of gozerbot is now (\d+)')

def handle_karmaup2(bot, ievent):
    """ increase karma without reason """
    ievent.groups += [None, ]
    handle_karmaup(bot, ievent)

rebefore.add(9, '^(.+)\+\+$', handle_karmaup2, ['USER', 'ANONKARMA'], \
allowqueue=False)

def handle_karmadown(bot, ievent):
    """ <item>-- ['#' <reason> .. decrease karma item with reason """
    if not ratelimit(bot, ievent):
        return
    (item, reason) = ievent.groups
    item = item.strip().lower()
    if not item:
        return
    karma.down(item, reason=reason)
    karma.setwhodown(item, ievent.nick)
    ievent.reply('karma of ' + item + ' is now ' + str(karma.get(item)))

rebefore.add(8, '^(.+)\-\-\s+#(.*)$', handle_karmadown, ['USER', 'KARMA', \
'ANONKARMA'], allowqueue=False)
examples.add('--', "<item>-- ['#' <reason>] .. lower karma of item with 1 \
(use optional reason)", '1) gozerbot-- 2) gozerbot-- # bad bot')
tests.add('miep--', 'karma of miep is now (-\d+)')
tests.add('miep-- # top bot', 'karma of miep is now (-\d+)')

def handle_karmadown2(bot, ievent):
    """ decrease karma item without reason """
    ievent.groups += [None, ]
    handle_karmadown(bot, ievent)

rebefore.add(9, '^(.+)\-\-$', handle_karmadown2, ['USER', 'KARMA', \
'ANONKARMA'], allowqueue=False)

def handle_karmawhyup(bot, ievent):
    """ karma-whyup <item> .. show why karma of item has been increased """
    if not ievent.rest:
        ievent.missing('<item>')
        return
    item = ievent.rest
    result = karma.whykarmaup(item)
    if result:
        ievent.reply('whykarmaup of %s: ' % item, result, dot=True)
    else:
        ievent.reply('%s has no reason for karmaup yet' % item)

cmnds.add('karma-whyup', handle_karmawhyup, ['USER', 'WEB', \
'ANONKARMA'])
examples.add('karma-whyup', 'karma-whyup <item> .. show the reason why \
karma of <item> was raised', 'karma-whyup gozerbot')
aliases.data['wku'] = 'karma-whyup'
tests.add('gozerbot++ # top bot').add('karma-whyup gozerbot', 'top bot')

def handle_whykarmadown(bot, ievent):
    """ karma-whydown <item> .. show why karma of item has been decreased """
    if not ievent.rest:
        ievent.missing('<item>')
        return
    item = ievent.rest
    result = karma.whykarmadown(item)
    if result:
        ievent.reply('whykarmadown of %s: ' % item, result, dot=True)
    else:
        ievent.reply('%s has no reason for karmadown yet' % item)

cmnds.add('karma-whydown', handle_whykarmadown, ['USER', 'WEB', \
'ANONKARMA'])
examples.add('karma-whydown', 'karma-whydown <item> .. show the reason why \
karma of <item> was lowered', 'karma-whydown gozerbot')
aliases.data['wkd'] = 'karma-whydown'
tests.add('miep-- # kut bot').add('karma-whydown miep', 'kut bot')

def handle_karmagood(bot, ievent):
    """ karma-good .. show top 10 karma items """
    result = karma.good(limit=10)
    if result:
        res = []
        for i in result:
            if i[1] > 0:
                res.append("%s=%s" % (i[0], i[1]))
        ievent.reply('goodness: ', res, dot=True)
    else:
        ievent.reply('karma void')

cmnds.add('karma-good', handle_karmagood, ['USER', 'WEB', 'ANONKARMA', 'CLOUD'])
examples.add('karma-good', 'show top 10 karma', 'karma-good')
aliases.data['good'] = 'karma-good'
tests.add('gozerbot++').add('karma-good', 'gozerbot')

def handle_karmabad(bot, ievent):
    """ karma-bad .. show 10 most negative karma items """
    result = karma.bad(limit=10)
    if result:
        res = []
        for i in result:
            if i[1] < 0:
                res.append("%s=%s" % (i[0], i[1]))
        ievent.reply('badness: ', res, dot=True)
    else:
        ievent.reply('karma void')

cmnds.add('karma-bad', handle_karmabad, ['USER', 'WEB', 'ANONKARMA', 'CLOUD'])
examples.add('karma-bad', 'show lowest top 10 karma', 'karma-bad')
aliases.data['bad'] = 'karma-bad'
tests.add('miep--').add('karma-bad', 'miep')

def handle_whokarmaup(bot, ievent):
    """ karma-whoup <item> .. show who increased a karma item """
    if not ievent.rest:
        ievent.missing('<item>')
        return
    item = ievent.rest
    result = karma.getwhoup(item)
    statdict = Statdict()
    if result:
        for i in result:
            statdict.upitem(i)
        res = []
        for i in statdict.top():
            res.append("%s=%s" % i)
        ievent.reply("whokarmaup of %s: " % item, res, dot=True)
    else:
        ievent.reply('no whokarmaup data available for %s' % item)

cmnds.add('karma-whoup', handle_whokarmaup, ['USER', 'WEB', \
'ANONKARMA', 'CLOUD'])
examples.add('karma-whoup', 'karma-whoup <item> .. show who raised the \
karma of <item>', 'karma-whoup gozerbot')
tests.add('gozerbot++').add('karma-whoup gozerbot', '{{ me }}')

def handle_whokarmadown(bot, ievent):
    """ karma-whodown <item> .. show who decreased a karma item """
    if not ievent.rest:
        ievent.missing('<item>')
        return
    item = ievent.rest
    result = karma.getwhodown(item)
    statdict = Statdict()
    if result:
        for i in result:
            statdict.upitem(i)
        res = []
        for i in statdict.top():
            res.append("%s=%s" % i)
        ievent.reply("whokarmadown of %s: " % item, res, dot=True)
    else:
        ievent.reply('no whokarmadown data available for %s' % item)

cmnds.add('karma-whodown', handle_whokarmadown, ['USER', 'WEB', \
'ANONKARMA', 'CLOUD'])
examples.add('karma-whodown', 'karma-whodown <item> .. show who lowered \
the karma of <item>', 'karma-whodown gozerbot')
tests.add('miep--').add('karma-whodown miep', '{{ me }}')

def handle_karmasearch(bot, ievent):
    """ karma-search <txt> .. search for karma items """
    what = ievent.rest
    if not what:
        ievent.missing('<txt>')
        return
    result = karma.search(what)
    if result:
        res = []
        for i in result:
            res.append("%s (%s)" % (i.item, i.value))
        ievent.reply("karma items matching %s: " % what, res, dot=True)
    else:
        ievent.reply('no karma items matching %s found' % what)

cmnds.add('karma-search', handle_karmasearch, ['USER', 'WEB', \
'ANONKARMA', 'CLOUD'])
examples.add('karma-search', 'karma-search <txt> .. search karma' , \
'karma-search gozerbot')
tests.add('gozerbot++').add('karma-search gozer', 'gozerbot')

def handle_karmawhatup(bot, ievent):
    """ show what karma items have been upped by nick """
    try:
        nick = ievent.args[0]
    except IndexError:
        ievent.missing('<nick>')
        return
    result = karma.whatup(nick)
    if result:
        res = []
        for i in result:
            res.append("%s (%s)" % i)
        ievent.reply("karma items upped by %s: " % nick, res, dot=True)
    else:
        ievent.reply('no karma items upped by %s' % nick)

cmnds.add('karma-whatup', handle_karmawhatup, ['USER', 'WEB', \
'ANONKARMA', 'CLOUD'])
examples.add('karma-whatup', 'karma-whatup <nick> .. show what karma items \
<nick> has upped' , 'karma-whatup dunker')
tests.add('gozerbot++').add('karma-whatup {{ me }}', 'gozerbot')

def handle_karmawhatdown(bot, ievent):
    """ show what karma items have been lowered by nick """
    try:
        nick = ievent.args[0]
    except IndexError:
        ievent.missing('<nick>')
        return
    result = karma.whatdown(nick)
    if result:
        res = []
        for i in result:
            res.append("%s (%s)" % i)
        ievent.reply("karma items downed by %s: " % nick, res, dot=True)
    else:
        ievent.reply('no karma items downed by %s' % nick)

cmnds.add('karma-whatdown', handle_karmawhatdown, ['USER', 'WEB', \
'ANONKARMA', 'CLOUD'])
examples.add('karma-whatdown', 'karma-whatdown <nick> .. show what karma \
items <nick> has downed' , 'karma-whatdown dunker')
tests.add('miep--').add('karma-whatdown {{ me }}', 'miep')
