# plugs/infoitem.py
#
#

""" information items .. keyword/description pairs """

__copyright__ = 'this file is in the public domain'

from gozerbot.tests import tests
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.redispatcher import rebefore, reafter
from gozerbot.ignore import shouldignore
from gozerbot.datadir import datadir
from gozerbot.persist.persist import Persist
from gozerbot.generic import lockdec, cchar, rlog, handle_exception
from gozerbot.aliases import aliases
from gozerbot.plughelp import plughelp
from gozerbot.callbacks import callbacks
from gozerbot.users import users
from gozerbot.config import config
from gozerbot.database.alchemy import Base, create_session, trans
from datetime import datetime
from time import localtime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Sequence
import sqlalchemy as sa

class InfoItems(Base):
    __tablename__ = 'infoitems'
    __table_args__ = {'useexisting': True}
    indx = Column('indx', Integer, Sequence('infoitems_indx_seq', optional=True), primary_key=True)
    item = Column('item', String(255), nullable=False)
    description = Column('description', Text, nullable=False)
    userhost = Column('userhost', String(255), ForeignKey('userhosts.userhost'), nullable=False)
    time = Column('time', DateTime, nullable=False)

    def __init__(self, item, description, userhost, ttime=None):
        self.time = ttime and ttime or datetime.now()
        self.item = item.lower()
        self.description = description
        self.userhost = userhost

## BEGIN UPGRADE PART

def upgrade():
    rlog(10, 'infoitem', 'upgrading')
    teller = 0
    dbdir = datadir + os.sep + 'db' + os.sep + 'infoitem.db'
    if os.path.exists(dbdir):
        try:
            from gozerbot.database.db import Db
            db = Db(dbtype='sqlite')
            db.connect('db/infoitem.db')
            result = db.execute(""" SELECT * FROM infoitems """)
            if result:
                for i in result:
                    info.add(*i[1:])
                    teller += 1
        except Exception, ex:
            handle_exception()
    else:
        oldfile = datadir + os.sep + 'old' + os.sep + 'infoitems'
        try:
            from gozerbot.utils.generic import dosed
            from gozerbot.compat.persist import Persist
            dosed(oldfile, 's/cgozerbot\.compat/cgozerplugs/')
            oldinfo = Persist(oldfile)
            assert(oldinfo)
            if not oldinfo.data:
                return
            for item, descrlist in oldinfo.data.iteritems():
                for descr in descrlist:
                    info.add(item, descr, 'none', 0)
                    teller += 1
        except IOError, ex:
            if "No such file" in str(ex):
                rlog(10, 'infoitem', 'nothing to upgrade')
        except Exception, ex:
            rlog(10, 'infoitem', "can't upgrade: %s" % str(ex))
            return
    rlog(10, 'infoitem', 'upgraded %s infoitems' % str(teller))
    return teller

import thread, os, time

plughelp.add('infoitem', 'also known as factoids .. info can be retrieved \
by keyword or searched')

infolock = thread.allocate_lock()

# create lock descriptor
locked = lockdec(infolock)

class InfoitemsDb(object):

    """ information items """

    @trans 
    def add(self, session, item, description, userhost, ttime):
        """ add an item """
        item = item.lower()
        result = 0
        try:
            newitem = InfoItems(item, description, userhost, datetime.fromtimestamp(ttime))
            session.add(newitem)
            result = 1
        except Exception, ex:
            rlog(10, 'infoitem', "can't add item: %s" % str(ex))
            raise ex
        return result

    def get(self, item):
        """ get infoitems """
        s = create_session()
        item = item.lower()
        result = [r.description for r in s.query(InfoItems).filter_by(item=item)]
        return result

    @trans
    def delete(self, session, indexnr):
        """ delete item with indexnr  """
        item = session.query(InfoItems).filter_by(indx=indexnr).first()
        try:
            session.delete(item)
            result = 1
        except Exception, ex:
            rlog(10, 'infoitem', "can't delete item %s: %s" % (str(indexnr), str(ex)))
            raise ex
        return result

    @trans
    def deltxt(self, session, item, txt):
        """ delete item with matching txt """
        items = session.query(InfoItems).filter(InfoItems.item==item.lower
                        ).filter(InfoItems.description.like('%%%s%%' % txt))
        result = 0
        try:
            for n, i in enumerate(items):
                session.delete(i)
                result = n + 1
        except Exception, ex:
            rlog(10, 'infoitem', "can't delete items like %s: %s" % (str(txt), str(ex)))
            raise ex
        return result

    def size(self):
        """ return number of items """
        s = create_session()
        count = s.query(sa.func.count(InfoItems.indx)).first()[0]
        return count

    def searchitem(self, search):
        """ search items """
        s = create_session() 
        result = s.query(InfoItems).filter(InfoItems.item.like('%%%s%%' % search))
        return result

    def searchdescr(self, search):
        """ search descriptions """
        s = create_session()
        result = s.query(InfoItems).filter(InfoItems.description.like('%%%s%%' % search))
        return result


info = InfoitemsDb()
Base.metadata.create_all()
assert(info)

def size():
    """ return number of infoitems """
    return info.size()

def search(what, queue):
    rlog(10, 'infoitem', 'searched for %s' % what)
    result = info.searchitem(what)   
    if not result:
        return
    res = []
    for i in result:
        queue.put_nowait(i.description)
    result = info.searchdescr(what)   
    if not result:
        return
    for i in result:
        queue.put_nowait("[%s] %s" % (i.item, i.description))

def infopre(bot, ievent):
    """ see if info callback needs to be called """
    cc = cchar(bot, ievent)
    if ievent.origtxt and  ievent.origtxt[0] in cc and not ievent.usercmnd \
and ievent.txt:
        return 1

def infocb(bot, ievent):
    """ implement a !infoitem callback """
    if not shouldignore(ievent.userhost):
        if 'handle_question' in bot.state['allowed'] or users.allowed(ievent.userhost, 'USER'):
             data = info.get(ievent.txt)
             if data:
                ievent.reply('%s is ' % ievent.txt, data , dot=True)

callbacks.add('PRIVMSG', infocb, infopre)

def handle_infoupgrade(bot, ievent):
    if info.size():
         if '-f' in ievent.optionset:
             pass
         else:
             ievent.reply('there are already infoitems in the main database .. not upgrading')
             ievent.reply('use the -f option to force an upgrade')
             return
    ievent.reply('upgrading infoitems')
    nritems = upgrade()
    ievent.reply('%s items upgraded' % nritems)

cmnds.add('info-upgrade', handle_infoupgrade, 'OPER', options={'-f': ''})

def handle_infosize(bot, ievent):
    """ info-size .. show number of information items """
    ievent.reply("we have %s infoitems" % info.size())

cmnds.add('info-size', handle_infosize, ['USER', 'WEB', 'CLOUD'])
examples.add('info-size', 'show number of infoitems', 'info-size')
tests.add('info-size', 'we have (\d+) infoitems')

def handle_addinfoitem(bot, ievent):
    """ <keyword> = <description> .. add information item """
    try:
        (what, description) = ievent.groups
    except ValueError:
        ievent.reply('i need <item> <description>')
        return
    if len(description) < 3:
        ievent.reply('i need at least 3 chars for the description')
        return
    what = what.strip()
    ret = info.add(what, description, ievent.userhost, time.time())
    if ret:
        ievent.reply('item added')
    else:
        ievent.reply('unable to add item')

rebefore.add(10, '^(.+?)\s+=\s+(.+)$', handle_addinfoitem, ['USER', \
'INFOADD'], allowqueue=False)
examples.add('=', 'add description to item', 'dunk = top')
tests.add('gozerbot = top bot', 'item added')

def handle_question(bot, ievent):
    """ <keyword>? .. ask for information item description """
    try:
        what = ievent.groups[0]
    except IndexError:
        ievent.reply('i need a argument')
        return
    what = what.strip().lower()
    infoitems = info.get(what)
    if infoitems:
        ievent.reply("%s is " % what, infoitems, dot=True)
    else:
        ievent.reply('nothing known about %s' % what)

reafter.add(10, '^(.+)\?$', handle_question, ['USER', 'WEB', 'JCOLL', \
'CLOUD'], allowqueue=True)
reafter.add(10, '^\?(.+)$', handle_question, ['USER', 'WEB', 'JCOLL', \
'CLOUD'], allowqueue=True)
examples.add('?', 'show infoitems of <what>', '1) test? 2) ?test')
tests.add('gozerbot?', 'top bot')
tests.add('?gozerbot', 'top bot')

def handle_forget(bot, ievent):
    """ forget <keyword> <txttomatch> .. remove information item where \
        description matches txt given """
    if len(ievent.args) > 1:
        what = ' '.join(ievent.args[:-1])
        txt = ievent.args[-1]
    else:
        ievent.missing('<item> <txttomatch> (min 3 chars)')
        return
    if len(txt) < 3:
        ievent.reply('i need txt with at least 3 characters')
        return
    what = what.strip().lower()
    try:
        nrtimes = info.deltxt(what, txt)
    except KeyError:
        ievent.reply('no records matching %s found' % what)
        return
    if nrtimes:
        ievent.reply('item deleted')
    else:
        ievent.reply('delete %s of %s failed' % (txt, what))

cmnds.add('info-forget', handle_forget, ['FORGET', 'OPER'])
examples.add('info-forget', 'forget <item> containing <txt>', 'info-forget \
dunk bla')
aliases.data['forget'] = 'info-forget'
tests.add('gozerbot = top bot').add('info-forget gozerbot top', 'item deleted')

def handle_searchdescr(bot, ievent):
    """ info-sd <txttosearchfor> .. search information items descriptions """
    if not ievent.rest:
        ievent.missing('<txt>')
        return
    else:
        what = ievent.rest
    what = what.strip().lower()
    result = info.searchdescr(what)
    if result: 
        res = []
        for i in result:
            res.append("[%s] %s" % (i.item, i.description))
        ievent.reply("the following matches %s: " % what, res, dot=True)
    else:
        ievent.reply('none found')

cmnds.add('info-sd', handle_searchdescr, ['USER', 'WEB', 'CLOUD'])
examples.add('info-sd', 'info-sd <txt> ..  search description of \
infoitems', 'info-sd http')
aliases.data['sd'] = 'info-sd'
aliases.data['sl'] = 'info-sd'
tests.add('gozerbot = top bot').add('info-sd top', 'top bot').end()

def handle_searchitem(bot, ievent):
    """ info-si <txt> .. search information keywords """
    if not ievent.rest:
        ievent.missing('<txt>')
        return
    else:
        what = ievent.rest
    what = what.strip().lower()
    result = info.searchitem(what)
    if result:
        res = []
        for i in result:
            res.append("[%s] %s" % (i.item, i.description))
        ievent.reply("the following matches %s: " % what, res, dot=True)
    else:
        ievent.reply('none found')

cmnds.add('info-si', handle_searchitem, ['USER', 'WEB', 'CLOUD'])
examples.add('info-si', 'info-si <txt> ..  search the infoitems keys', \
'info-si test')
aliases.data['si'] = 'info-si'
tests.add('gozerbot = top bot').add('info-si gozer', 'gozerbot').end()
