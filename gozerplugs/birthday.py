# dbplugs/birthday.py
#
#

""" manage birthdays """

__copyright__ = 'this file is in the public domain'

from gozerbot.generic import getdaymonth, strtotime, elapsedstring, getwho, \
bdmonths, handle_exception
from gozerbot.tests import tests
from gozerbot.users import users
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
from gozerbot.aliases import aliases
from gozerbot.config import config
import time, re

from gozerbot.database.alchemy import Base, create_session, trans
from datetime import datetime
from time import localtime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Sequence
import sqlalchemy as sa

class Birthday(Base):
    __tablename__ = 'birthday'
    __table_args__ = {'useexisting': True}
    name = Column('name', String(255), primary_key=True)
    birthday = Column('birthday', String(255), nullable=False)

    def __init__(self, name, birthday):
        self.name = name
        self.birthday = birthday

Base.metadata.create_all()

plughelp.add('birthday', 'manage birthday data')

def handle_bdset(bot, ievent):
    """ bd-set <date> .. set birthday """
    try:
        what = ievent.args[0]
        if not re.search('\d*\d-\d*\d-\d\d\d\d', what):
            ievent.reply('i need a date in the format day-month-year')
            return
    except IndexError:
        ievent.missing('<date>')
        return
    name = users.getname(ievent.userhost)
    s = create_session()
    s.begin(subtransactions=True)
    bd = s.query(Birthday).filter(Birthday.name==name).first()
    if not bd:
        bd = Birthday(name, what)
        s.save(bd)
    else:
        bd.birthday = what
    s.commit()
    ievent.reply('birthday set')

cmnds.add('bd-set', handle_bdset, 'USER')
examples.add('bd-set', 'bd-set <date> .. set birthday', 'bd-set 3-11-1967')
aliases.data['setbd'] = 'bd-set'
aliases.data['setjarig'] = 'bd-set'
tests.add('bd-set 3-11-1967', 'birthday set')

def handle_bddel(bot, ievent):
    """ bd-del .. delete birthday """
    name = users.getname(ievent.userhost)
    result = 0
    s = create_session()
    bd = s.query(Birthday).filter(Birthday.name==name).first()
    if not bd:
        ievent.reply('no birthday known for %s (%s)' % (ievent.nick, name))
    else:
        s.delete(bd)
        ievent.reply('birthday removed')

cmnds.add('bd-del', handle_bddel, 'USER')
examples.add('bd-del', 'delete birthday data', 'bd-del')
aliases.data['delbd'] = 'bd-del'
aliases.data['deljarig'] = 'bd-del'
tests.add('bd-del', 'birthday removed')

def handle_bd(bot, ievent):
    """ bd [<nr|user>] .. show birthday of month or user """
    if not ievent.rest:    
        handle_checkbd(bot, ievent)
        return
    try:
        int(ievent.args[0])
        handle_checkbd2(bot, ievent)
        return
    except (IndexError, ValueError):
        who = ievent.args[0].lower()
    userhost = getwho(bot, who)
    if not userhost:
        ievent.reply("don't know userhost of %s" % who)
        return
    name = users.getname(userhost)
    if not name:
        ievent.reply("can't find user for %s" % userhost)
        return
    s = create_session()
    bd = s.query(Birthday).filter(Birthday.name==name).first()
    if bd:
        ievent.reply('birthday of %s is %s' % (who, bd.birthday))
    else:
        ievent.reply('no birthday know for %s' % name)

cmnds.add('bd', handle_bd, ['USER', 'WEB'])
examples.add('bd', 'bd [<nr|user>] .. show birthdays for this month or \
show birthday of <nick>', '1) bd 2) bd dunker')
aliases.data['jarig'] = 'bd'
tests.add('bd-set 3-11-1967').add('bd 11', 'birthdays in Nov')

def handle_checkbd(bot, ievent):
    """ bd-check .. check birthdays for current month """
    (nowday, nowmonth) = getdaymonth(time.time())
    mstr = ""
    result = []
    s = create_session()
    bds = s.query(Birthday).all()
    if not bds:
        ievent.reply('no birthdays this month')
        return
    for i in bds:
        btime = strtotime(i.birthday)
        if btime == None:
            continue
        (day, month) = getdaymonth(btime)
        if month == nowmonth:
            result.append((int(day), i.name, i.birthday))
            if day == nowday and month == nowmonth:
                ievent.reply("it's %s's birthday today!" % i.name)
    result.sort(lambda x, y: cmp(x[0], y[0]))
    for i in result:
        mstr += "%s: %s " % (i[1], i[2])
    if mstr:
        mstr = "birthdays this month = " + mstr
        ievent.reply(mstr)
    else:
        ievent.reply('no birthdays this month')

def handle_checkbd2(bot, ievent):
    """ bd-check <nr> .. show birthdays in month (by number) """
    try:
        monthnr = int(ievent.args[0])
        if monthnr < 1 or monthnr > 12:
            ievent.reply("number must be between 1 and 12")
            return
    except (IndexError, ValueError):
        ievent.missing('<monthnr>')
        return
    mstr = ""
    result = []
    s = create_session()
    bds = s.query(Birthday).all()
    if not bds:
        ievent.reply('no birthdays known')
        return
    for i in bds:
        btime = strtotime(i.birthday)
        if btime == None:
            continue
        (day, month) = getdaymonth(btime)
        if month == bdmonths[monthnr]:
            result.append((int(day), i.name, i.birthday))
    result.sort(lambda x, y: cmp(x[0], y[0]))
    for i in result:
        mstr += "%s: %s " % (i[1], i[2])
    if mstr:
        mstr = "birthdays in %s = " % bdmonths[monthnr] + mstr
        ievent.reply(mstr)
    else:
        ievent.reply('no birthdays found for %s' % bdmonths[monthnr])

def handle_age(bot, ievent):
    """ age <nick> .. show age of user """
    try:
        who = ievent.args[0].lower()
    except IndexError:
        ievent.missing('<nick>')
        return
    userhost = getwho(bot, who)
    if not userhost:
        ievent.reply("don't know userhost of %s" % who)
        return
    name = users.getname(userhost)
    if not name:
        ievent.reply("can't find user for %s" % userhost)
        return
    s = create_session()
    bd = s.query(Birthday).filter(Birthday.name==name).first()
    try:
        birthday = bd.birthday
    except (TypeError, AttributeError):
        ievent.reply("can't find birthday data for %s" % who)
        return
    btime = strtotime(birthday)
    if btime == None:
        ievent.reply("can't make a date out of %s" % birthday)
        return
    age = int(time.time()) - int(btime)
    ievent.reply("age of %s is %s" % (who, elapsedstring(age, ywd=True)))

cmnds.add('age', handle_age, ['USER', 'WEB'])
examples.add('age', 'age <nick> .. show how old <nick> is', 'age dunker')
aliases.data['oud'] = 'age'
tests.add('bd-set 3-11-1967').add('age {{ me }}', 'age of {{ me }} is')
