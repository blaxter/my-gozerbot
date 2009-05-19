# plugs/quote.py
#
#

__copyright__ = 'this file is in the public domain'
__depend__ = ['karma', ]
__depending__ = ['grab', ]

from gozerbot.tests import tests
from gozerbot.persist.persist import Persist
from gozerbot.utils.nextid import nextid
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.datadir import datadir
from gozerbot.generic import lockdec, rlog, handle_exception
from gozerbot.plughelp import plughelp
from gozerbot.aliases import aliases
from gozerbot.config import config
from gozerplugs.karma import karma
import random, re, time, thread, os, types

from gozerbot.database.alchemy import Base, create_session, trans
from datetime import datetime
from time import localtime   
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Sequence
import sqlalchemy as sa

class Quotes(Base):
    __tablename__ = 'quotes'
    __table_args__ = {'useexisting': True }
    indx = Column('indx', Integer, Sequence('quotes_indx_seq', optional=True), primary_key=True)
    quote = Column('quote', Text, nullable=False)
    userhost = Column('userhost', String(255), ForeignKey('userhosts.userhost'), nullable=False)
    createtime = Column('createtime', DateTime, nullable=False)
    nick = Column('nick', String(255), nullable=False)

    def __init__(self, quote, userhost, createtime, nick):
        self.quote = quote
        self.userhost = userhost
        self.createtime = createtime
        self.nick = nick

## UPGRADE PART

def upgrade():
    rlog(10, 'quote', 'upgrading')
    teller = 0
    oldfile = datadir + os.sep + 'old' + os.sep + 'quotes'
    dbdir = datadir + os.sep + 'db' + os.sep + 'quote.db'
    if os.path.exists(dbdir):
        try:
            from gozerbot.database.db import Db
            db = Db(dbtype='sqlite')
            db.connect('db/quote.db')
            result = db.execute(""" SELECT * FROM quotes """)
            if result:
                for i in result:
                    try:
                        quotes.add(i[4], i[2], i[1], i[3])
                    except:
                        quotes.add(i[3], i[2], i[1], i[4])
                    teller += 1
        except Exception, ex:
            handle_exception()
        return teller
    try:
        from gozerbot.utils.generic import dosed   
        from gozerbot.compat.persist import Persist
        from gozerbot.compat.todo import Todoitem
        dosed(oldfile, 's/cgozerbot\.compat/cgozerplugs/')
        oldpersist = Persist(oldfile) 
        if not oldpersist or not oldpersist.data:
            return
        for item in oldpersist.data:
            quotes.add(item.nick, item.userhost, item.quote)
            teller += 1
    except IOError, ex:
        if "No such file" in str(ex):
            rlog(10, 'quote', 'nothing to upgrade')
    except Exception, ex:
        rlog(10, 'quote', "can't upgrade .. reason: %s" % str(ex))
        handle_exception()
    else:
        rlog(10, 'quote', "upgraded %s items" % teller)

# END UPGRADE PART

plughelp.add('quote', 'manage quotes')

class QuotesDb(object):

    """ quotes db interface """

    def size(self):
        """ return number of items """
        s = create_session()
        count = s.query(sa.func.count(Quotes.indx)).first()[0]
        return count

    @trans
    def add(self, session, nick, userhost, quote, ttime=None):
        """ add a quote """
        if ttime:
            try:
                ttime = float(ttime)
            except TypeError:
                pass
            t = datetime.fromtimestamp(ttime)
        else: 
            t = datetime.now()
        quote = Quotes(quote, userhost, t, nick)
        session.add(quote)
        session.commit()
        return quote.indx

    @trans
    def delete(self, session, quotenr):
        quote = session.query(Quotes).filter(Quotes.indx==quotenr).first()
        if quote:
             session.delete(quote)
             return 1

    def random(self):
        """ get random quote """
        s = create_session()
        result = s.query(Quotes.indx)
        indices = []
        if not result:
            return []
        for i in result:
            indices.append(i[0])
        if indices:
            idnr = random.choice(indices)
            return self.idquote(idnr)

    def idquote(self, quotenr):
        """ get quote by id """
        s = create_session()
        quote = s.query(Quotes).filter(Quotes.indx==quotenr).first()
        if quote:
            return quote

    def whoquote(self, quotenr):
        """ get who quoted the quote """
        s = create_session()
        quote = s.query(Quotes).filter(Quotes.indx==quotenr).first()
        if quote:
            return quote

    def last(self, nr=1):
        """ get last quote """ 
        s = create_session()
        result = s.query(Quotes).order_by(Quotes.indx.desc()).limit(nr)
        if result:
            return result

    def search(self, what):
        """ search quotes """
        s = create_session()
        result = s.query(Quotes).filter(Quotes.quote.like('%%%s%%' % what)).all()
        if result:
            return result

    def searchlast(self, what, nr):
        """ search quotes """
        s = create_session()
        result = s.query(Quotes).filter(Quotes.quote.like('%%%s%%' % what)).order_by(Quotes.indx.desc()).limit(nr)
        if result:
            return result

quotes = QuotesDb()
Base.metadata.create_all()
assert(quotes)

def size():
    """ return number of quotes """
    return quotes.size()

def search(what, queue):
    """ search the quotes """
    rlog(10, 'quote', 'searched for %s' % what)
    result = quotes.search(what)
    for i in result:
        queue.put_nowait("#%s %s" % (i.indx, i.quote))

def handle_quoteupgrade(bot, ievent):
    if quotes.size():
         if '-f' in ievent.optionset:
             pass
         else:   
             ievent.reply('there are already quote items in the main database .. not upgrading')
             ievent.reply('use the -f option to force an upgrade')
             return
    ievent.reply('upgrading quotes')
    nritems = upgrade()
    ievent.reply('%s items upgraded' % nritems)

cmnds.add('quote-upgrade', handle_quoteupgrade, 'OPER', options={'-f': ''})

def handle_quoteadd(bot, ievent):
    """ quote-add <txt> .. add a quote """
    if not ievent.rest:
        ievent.missing("<quote>")
        return
    idnr = quotes.add(ievent.nick, ievent.userhost, ievent.rest)
    ievent.reply('quote %s added' % idnr)

cmnds.add('quote-add', handle_quoteadd, ['USER', 'QUOTEADD'], allowqueue=False)
examples.add('quote-add', 'quote-add <txt> .. add quote', 'quote-add mekker')
aliases.data['aq'] = 'quote-add'
tests.add('quote-add mekker','quote (\d+) added')

def handle_quotewho(bot, ievent):
    """ quote-who <nr> .. show who added a quote """
    try:
        quotenr = int(ievent.args[0])
    except IndexError:
        ievent.missing("<nr>")
        return
    except ValueError:
        ievent.reply("argument must be an integer")
        return
    result = quotes.whoquote(quotenr)
    if not result:
        ievent.reply('no who quote data available')
        return
    if result.createtime:
        if type(result.createtime) == types.LongType:
            ievent.reply('quote #%s was made by %s on %s' % (quotenr, \
result.nick, datetime.fromtimestamp(result.createtime).ctime()))
        else:
            ievent.reply('quote #%s was made by %s on %s' % (quotenr, \
result.nick, result.createtime.ctime()))
    else:
        ievent.reply('quote #%s was made by %s' % (quotenr, result.nick))

cmnds.add('quote-who', handle_quotewho, ['USER', 'WEB', 'CLOUD', 'ANONQUOTE'])
examples.add('quote-who', 'quote-who <nr> .. show who quote <nr>', \
'quote-who 1')
aliases.data['wq'] = 'quote-who'
tests.add('quote-who 1', 'quote #(\d+) was made by (\S+)').end()

def handle_quotedel(bot, ievent):
    """ quote-del <nr> .. delete quote by id """
    try:
        quotenr = int(ievent.args[0])
    except IndexError:
        ievent.missing('<nr>')
        return
    except ValueError:
        ievent.reply('argument needs to be an integer')
        return
    if quotes.delete(quotenr):
        ievent.reply('quote %s deleted' % quotenr)
    else:
        ievent.reply("can't delete quote with nr %s" % quotenr)

cmnds.add('quote-del', handle_quotedel, ['QUOTEDEL', 'OPER', 'QUOTE'])
examples.add('quote-del', 'quote-del <nr> .. delete quote', 'quote-del 2')
aliases.data['dq'] = 'quote-del'
tests.add('quote-add mekker', 'quote (\d+)').add('quote-del %s', 'quote %s deleted').end()

def handle_quotelast(bot, ievent):
    """ quote-last .. show last quote """
    search = ""
    try:
        (nr, search) = ievent.args
        nr = int(nr)  
    except ValueError:
        try:
            nr = ievent.args[0]
            nr = int(nr)
        except (IndexError, ValueError):
            nr = 1
            try:
                search = ievent.args[0]
            except IndexError:
                search = ""
    if nr < 1 or nr > 4:
        ievent.reply('nr needs to be between 1 and 4')
        return
    search = re.sub('^d', '', search)
    if search:
        quotelist = quotes.searchlast(search, nr)
    else:
        quotelist = quotes.last(nr)
    if quotelist != None:
        for quote in quotelist:
            try:
                qkarma = karma.get('quote %s' % quote.indx)
                if qkarma:
                    ievent.reply('#%s (%s) %s' % (quote.indx, qkarma, quote.quote))
                else:
                    ievent.reply('#%s %s' % (quote.indx, quote.quote))
            except AttributeError:
                    ievent.reply('#%s %s' % (quote.indx, quote.quote))
    else:
        ievent.reply("can't fetch quote")

cmnds.add('quote-last', handle_quotelast, ['USER', 'WEB', 'ANONQUOTE', 'CLOUD'])
examples.add('quote-last', 'show last quote', 'quote-last')
aliases.data['lq'] = 'quote-last'
tests.add('quote-last', '#(\d+)')

def handle_quote2(bot, ievent):
    """ quote-2 .. show 2 random quotes """
    quote = quotes.random()
    if quote:
        qkarma = karma.get('quote %s' % quote.indx)
        if qkarma:
            ievent.reply('#%s (%s) %s' % (quote.indx, qkarma, quote.quote))
        else:
            ievent.reply('#%s %s' % (quote.indx, quote.quote))
    else:
        ievent.reply('no quotes yet')
        return
    quote = quotes.random()
    if quote:
        qkarma = karma.get('quote %s' % quote.indx)
        if qkarma:
            ievent.reply('#%s (%s) %s' % (quote.indx, qkarma, quote.quote))
        else:
            ievent.reply('#%s %s' % (quote.indx, quote.quote))

cmnds.add('quote-2', handle_quote2, ['USER', 'WEB', 'ANONQUOTE', 'CLOUD'])
examples.add('quote-2', 'quote-2 .. show 2 random quotes', 'quote-2')
aliases.data['2q'] = 'quote-2'
tests.add('quote-2', '#(\d+)')
aliases.data['3q'] = "quote && quote && quote"

def handle_quoteid(bot, ievent):
    """ quote-id <nr> .. show quote by id """
    try:
        quotenr = int(ievent.args[0])
    except IndexError:
        ievent.missing('<nr>')
        return
    except ValueError:
        ievent.reply('argument must be an integer')
        return
    quote = quotes.idquote(quotenr)
    if quote:
        qkarma = karma.get('quote %s' % quote.indx)
        if qkarma:
            ievent.reply('#%s (%s) %s' % (quote.indx, qkarma, quote.quote))
        else:
            ievent.reply('#%s %s' % (quote.indx, quote.quote))
    else:
        ievent.reply("can't fetch quote with id %s" % quotenr)

cmnds.add('quote-id', handle_quoteid, ['USER', 'WEB', 'ANONQUOTE', 'CLOUD'])
examples.add('quote-id', 'quote-id <nr> .. get quote <nr>', 'quote-id 2')
aliases.data['iq'] = 'quote-id'
tests.add('quote-id 1', '#(\d+)')

def handle_quote(bot, ievent):
    """ quote .. show random quote """
    quote = quotes.random()
    if quote:
        qkarma = karma.get('quote %s' % quote.indx)
        if qkarma:
            ievent.reply('#%s (%s) %s' % (quote.indx, qkarma, quote.quote))
        else:
            ievent.reply('#%s %s' % (quote.indx, quote.quote))
    else:
        ievent.reply('no quotes yet')

cmnds.add('quote', handle_quote, ['USER', 'WEB', 'ANONQUOTE', 'CLOUD'])
examples.add('quote', 'show random quote', 'quote')
aliases.data['q'] = 'quote'
tests.add('quote', '#(\d+)')

def handle_quotesearch(bot, ievent):
    """ quote-search <txt> .. search quotes """
    if not ievent.rest:
        ievent.missing('<item>')
        return
    else:
        what = ievent.rest
        nrtimes = 3
    result = quotes.search(what)
    if result:
        if ievent.queues:
            res = []
            for quote in result:
                res.append('#%s %s' % (quote.indx, quote.quote))
            ievent.reply(res)
            return            
        if nrtimes > len(result):
            nrtimes = len(result)
        randquotes = random.sample(result, nrtimes)
        for quote in randquotes:
            qkarma = karma.get('quote %s' % quote.indx)
            if qkarma:
                ievent.reply('#%s (%s) %s' % (quote.indx, qkarma, quote.quote))
            else:
                ievent.reply("#%s %s" % (quote.indx, quote.quote))
    else:
        ievent.reply('no quotes found with %s' % what)

cmnds.add('quote-search', handle_quotesearch, ['USER', 'WEB', \
'ANONQUOTE', 'CLOUD'])
examples.add('quote-search', 'quote-search <txt> .. search quotes for <txt>'\
, 'quote-search bla')
aliases.data['sq'] = 'quote-search'
tests.add('quote-add gozerbot is tof').add('quote-search gozerbot', 'tof').end()

def handle_quotescount(bot, ievent):
    """ quote-count .. show number of quotes """
    ievent.reply('quotes count is %s' % quotes.size())

cmnds.add('quote-count', handle_quotescount, ['USER', 'WEB', \
'ANONQUOTE', 'CLOUD'])
examples.add('quote-count', 'count nr of quotes', 'quote-count')
aliases.data['cq'] = 'quote-count'
tests.add('quote-count', 'quotes count is (\d+)')

def handle_quotegood(bot, ievent):
    """ show top ten positive karma """
    result = karma.quotegood(limit=10)
    if result:
        resultstr = ""
        for i in result:
            if i[1] > 0:
                resultstr += "%s: %s " % (i[0], i[1])
        ievent.reply('quote goodness: %s' % resultstr)
    else:
        ievent.reply('quote karma void')

cmnds.add('quote-good', handle_quotegood, ['USER', 'WEB', 'ANONQUOTE', 'CLOUD'])
examples.add('quote-good', 'show top 10 quote karma', 'quote-good')
tests.add('quote 1++').add('quote-good', 'quote goodness').end()

def handle_quotebad(bot, ievent):
    """ show top ten negative karma """
    result = karma.quotebad(limit=10)
    if result:
        resultstr = ""
        for i in result:
            if i[1] < 0:
                resultstr += "%s: %s " % (i[0], i[1])
        ievent.reply('quote badness: %s' % resultstr)
    else:
        ievent.reply('quote karma void')

cmnds.add('quote-bad', handle_quotebad, ['USER', 'WEB', 'ANONQUOTE', 'CLOUD'])
examples.add('quote-bad', 'show lowest 10 quote karma', 'quote-bad')
tests.add('quote 2--').add('quote-bad', 'quote badness').end()
