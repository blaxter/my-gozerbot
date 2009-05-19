# dbplugs/lists.py
#
#
#

""" lists per global/channel/user """

__copyright__ = 'this file is in the public domain'

from gozerbot.tests import tests
from gozerbot.generic import handle_exception
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
from gozerbot.users import users
from gozerbot.config import config

from gozerbot.database.alchemy import Base, create_session, trans, transfunc
from datetime import datetime, timedelta
from time import localtime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Sequence
import sqlalchemy as sa

class Lists(Base):
    __tablename__ = 'list'
    __table_args__ = {'useexisting': True}
    indx = Column('indx', Integer, Sequence('list_indx_seq', optional=True), primary_key=True)
    username = Column('username', String(255), nullable=False)
    listname = Column('listname', String(255), nullable=False)
    item = Column('item', Text, nullable=False)

    def __init__(self, username, listname, item):
        self.username = username
        self.listname = listname
        self.item = item

plughelp.add('lists', 'maintain lists')

Base.metadata.create_all()

def size():
    """ return number of lists """
    def size(self):
        """ return number of todo's """
        s = create_session()
        count = s.query(sa.func.count(Lists.indx)).count()
        return count 

def getlists(username):
    """ get all lists of user """
    s = create_session()
    lists = s.query(Lists).filter(Lists.username==username)
    if lists:
        return lists

def getlist(username, listname):
    """ get list of user """
    s = create_session()
    lists = s.query(Lists).filter(Lists.username==username).filter(Lists.listname==listname)
    if lists:
        return lists

@transfunc
def addtolist(session, username, listname, item):
    """ add item to list """
    list = Lists(username, listname, item)
    session.add(list)
    session.commit()
    return list.indx

@transfunc
def delfromlist(session, username, indx):
    """ delete item from list """
    item = session.query(Lists).filter(Lists.username==username).filter(Lists.indx==indx).first()
    if item:
        session.delete(item)
        return 1

def mergelist(username, listname, l):
    """ merge 2 lists """
    teller = 0
    for i in l:
        addtolist(username, listname, i)
        teller += 1
    return teller

def handle_listsglobal(bot, ievent):
    """ lists <listname> [',' <item>] .. global lists"""
    if not ievent.rest:
        ievent.missing("<listname> [',' <item>]")
        return
    try:
        listname, item = ievent.rest.split(',', 1)
    except ValueError:
        l = getlist('all', ievent.rest)
        if not l:
            ievent.reply('no %s list available' % ievent.rest)
            return
        result = []
        for i in l:
            result.append("%s) %s" % (i.indx, i.item))
        ievent.reply(result)
        return
    listname = listname.strip().lower()
    item = item.strip()
    if not listname or not item:
        ievent.missing("<listname> [',' <item>]")
        return
    result = 0
    try:
        result = addtolist('all', listname, item)
    except Exception, ex:
        handle_exception()
        ievent.reply('ERROR: %s' % str(ex))
        return
    if result:
        ievent.reply('%s (%s) added to %s list' % (item, result, listname))
    else:
        ievent.reply('add failed')

cmnds.add('lists-global', handle_listsglobal, 'USER')
examples.add('lists-global', "lists-global <listname> [',' <item>] .. show \
content of list or add item to list", '1) lists-global bla 2) lists-global \
bla, mekker')
tests.add('lists-global test, mekker', 'added to test list').add('lists-global test', 'mekker')

def handle_listsglobaldel(bot, ievent):
    """ list-globaldel <listname> ',' <listofnrs> .. remove items with \
indexnr from list """
    if not ievent.rest:
        ievent.missing('<listofnrs>')
        return
    try:
        nrs = []
        for i in ievent.rest.split():
            nrs.append(int(i))
    except ValueError:
        ievent.reply('%s is not an integer' % i)
        return
    nrs.sort()
    failed = []
    itemsdeleted = 0
    try:
        for i in nrs:
            result = delfromlist('all', i)
            if not result:
                failed.append(str(i))
            else:
                itemsdeleted += 1
    except Exception, ex:
        handle_exception()
        ievent.reply('ERROR: %s' % str(ex))
        return
    if failed:
        ievent.reply('failed to delete %s' % ' '.join(failed))
    ievent.reply('%s item(s) removed' % itemsdeleted)

cmnds.add('lists-globaldel', handle_listsglobaldel, 'USER')
examples.add('lists-globaldel', "lists-globaldel <listname> ',' <listofnrs> \
.. remove items with indexnr from list", '1) lists-globaldel 1 2) \
lists-globaldel 0 3 6')
tests.add('lists-global test, mekker', '(\d+)\) added to test list').add('lists-globaldel %s', '1 item\(s\) removed')

def handle_listsglobalshow(bot, ievent):
    """ show avaiable global lists """
    l = getlists('all')
    if not l:
        ievent.reply('no lists available')
        return
    else:
        result = []
        for i in l:
            if not i.listname in result:
                result.append(i.listname)
        if result:
            ievent.reply(result, dot=True)

cmnds.add('lists-globalshow', handle_listsglobalshow, 'USER')
examples.add('lists-globalshow', 'show available global lists' , \
'lists-globalshow')
tests.add('lists-global test, mekker', 'added to test list').add('lists-globalshow', 'test')

def handle_listschan(bot, ievent):
    """ lists-chan <listname> [',' <item>] .. global lists"""
    if not ievent.rest:
        ievent.missing("<listname> [',' <item>]")
        return
    try:
        listname, item = ievent.rest.split(',', 1)
    except ValueError:
        l = getlist(ievent.channel, ievent.rest)
        if not l:
            ievent.reply('no %s list available' % ievent.rest)
            return
        result = []
        for i in l:
            result.append("%s) %s" % (i.indx, i.item))
        ievent.reply(result)
        return
    listname = listname.strip().lower()
    item = item.strip()
    if not listname or not item:
        ievent.missing("<listname> [',' <item>]")
        return
    result = 0
    try:
        result = addtolist(ievent.channel, listname, item)
    except Exception, ex:
        handle_exception()
        ievent.reply('ERROR: %s' % str(ex))
        return
    if result:
        ievent.reply('%s (%s) added to %s list' % (item, result, listname))
    else:
        ievent.reply('add failed')

cmnds.add('lists-chan', handle_listschan, 'USER')
examples.add('lists-chan', "lists-chan <listname> [',' <item>] .. show \
content of list or add item to list", '1) lists-chan bla 2) lists-chan \
bla, mekker')
tests.add('lists-chan test, mekker', 'added to test list').add('lists-chan test', 'mekker')

def handle_listschandel(bot, ievent):
    """ lists-chandel <listname> ',' <listofnrs> .. remove items with \
indexnr from list """
    if not ievent.rest:
        ievent.missing('<listofnrs>')
        return
    try:
        nrs = []
        for i in ievent.rest.split():
            nrs.append(int(i))
    except ValueError:
        ievent.reply('%s is not an integer' % i)
        return
    nrs.sort()
    failed = []
    itemsdeleted = 0
    try:
        for i in nrs:
            result = delfromlist(ievent.channel, i)
            if not result:
                failed.append(str(i))
            else:
                itemsdeleted += 1
    except Exception, ex:
        handle_exception()
        ievent.reply('ERROR: %s' % str(ex))
        return
    if failed:
        ievent.reply('failed to remove %s' % ' '.join(failed))
    ievent.reply('%s item(s) removed' % itemsdeleted)

cmnds.add('lists-chandel', handle_listschandel, 'USER')
examples.add('lists-chandel', "lists-chandel <listname> ',' <listofnrs> \
.. remove items with indexnr from list", '1) lists-chandel 1 2) \
lists-chandel 0 3 6')
tests.add('lists-chan test, mekker', '(\d+)\) added to test list').add('lists-chandel %s', '1 item\(s\) removed')

def handle_listschanshow(bot, ievent):
    """ show avaiable lists """
    l = getlists(ievent.channel)
    if not l:
        ievent.reply('no lists available')
        return
    else:
        result = []
        for i in l:
            if not i.listname in result:
                result.append(i.listname)
        if result:
            ievent.reply(result, dot=True)

cmnds.add('lists-chanshow', handle_listschanshow, 'USER')
examples.add('lists-chanshow', 'show available channel lists' , \
'lists-chanshow')
tests.add('lists-chan test, mekker').add('lists-chanshow', 'test')

def handle_lists(bot, ievent):
    """ lists <listname> [',' <item>] .. global lists"""
    if not ievent.rest:
        ievent.missing("<listname> [',' <item>]")
        return
    username = users.getname(ievent.userhost)
    try:
        listname, item = ievent.rest.split(',', 1)
    except ValueError:
        l = getlist(username, ievent.rest)
        if not l:
            ievent.reply('no %s list available' % ievent.rest)
            return
        result = []
        for i in l:
            result.append("%s) %s" % (i.indx, i.item))
        ievent.reply(result)
        return
    listname = listname.strip().lower()
    item = item.strip()
    if not listname or not item:
        ievent.missing("<listname> [',' <item>]")
        return
    result = 0
    try:
        result = addtolist(username, listname, item)
    except Exception, ex:
        handle_exception()
        ievent.reply('ERROR: %s' % str(ex))
        return
    if result:
        ievent.reply('%s (%s) added to %s list' % (item, result, listname))
    else:
        ievent.reply('add failed')

cmnds.add('lists', handle_lists, 'USER')
examples.add('lists', "lists <listname> [',' <item>] .. show content of list \
or add item to list", '1) lists bla 2) lists bla, mekker')
tests.add('lists test, mekker').add('lists test', 'mekker')

def handle_listsdel(bot, ievent):
    """ lists-del <listname> ',' <listofnrs> .. remove items with indexnr \
from list """
    if not ievent.rest:
        ievent.missing('<listofnrs>')
        return
    try:
        nrs = []
        for i in ievent.rest.split():
            nrs.append(int(i))
    except ValueError:
        ievent.reply('%s is not an integer' % i)
        return
    username = users.getname(ievent.userhost)
    nrs.sort()
    failed = []
    itemsdeleted = 0
    try:
        for i in nrs:
            result = delfromlist(username, i)
            if not result:
                failed.append(str(i))
            else:
                itemsdeleted += 1
    except Exception, ex:
        handle_exception()
        ievent.reply('ERROR: %s' % str(ex))
        return
    if failed:
        ievent.reply('failed to delete %s' % ' '.join(failed))
    ievent.reply('%s item(s) removed' % itemsdeleted)

cmnds.add('lists-del', handle_listsdel, 'USER')
examples.add('lists-del', "lists-del <listname> ',' <listofnrs> \
.. remove items with indexnr from list", '1) lists-del 1 2) \
lists-del 0 3 6')
tests.add('lists test, mekker', '(\d+)\) added to test list').add('lists-del %s', '1 item\(s\) removed')

def handle_listshow(bot, ievent):
    """ show avaiable lists """
    username = users.getname(ievent.userhost)
    l = getlists(username)
    if not l:
        ievent.reply('no lists available')
        return
    else:
        result = []
        for i in l:
            if not i.listname in result:
                result.append(i.listname)
        if result:
            ievent.reply(result, dot=True)

cmnds.add('lists-show', handle_listshow, 'USER')
examples.add('lists-show', 'show available channel lists' , 'lists-show')
tests.add('lists-chan test, mekker').add('lists-show', 'test')

def handle_listsmerge(bot, ievent):
    """ merge 2 lists """
    try:
        (fromlist, tolist) = ievent.args
    except ValueError:
        ievent.missing('<fromlist> <tolist>')
        return
    username = users.getname(ievent.userhost)
    res = getlist(username, fromlist)
    if not res: 
        ievent.reply('no %s list available or empty' % fromlist)
        return
    l = []
    for i in res:
        l.append(i.item)
    result = 0
    try:
        result = mergelist(username, tolist, l)
    except Exception, ex:
        handle_exception()
        ievent.reply('ERROR: %s' % str(ex))
        return
    ievent.reply('%s items merged' % result)

cmnds.add('lists-merge', handle_listsmerge, 'USER')
examples.add('lists-merge', 'lists-merge <fromlist> <tolist> .. merge 2 \
lists', 'lists-merge mekker miep')
tests.add('lists miep, mekker2').add('lists-merge test miep', '(\d+) items merged')
