# plugs/todo.py
#
#

""" manage todo lists .. by user or by channel .. a time/data string can 
 be provided to set time on a todo item.
"""

__copyright__ = 'this file is in the public domain'
__depend__ = ['alarm', ]

from gozerbot.generic import strtotime, striptime, getwho, today, lockdec, \
handle_exception, rlog
from gozerbot.tests import tests
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.users import users
from gozerbot.datadir import datadir
from gozerbot.persist.persist import PlugPersist
from gozerbot.plughelp import plughelp
from gozerbot.aliases import aliases
from gozerbot.config import config
from gozerplugs.alarm import alarms
import time, thread, os

from gozerbot.database.alchemy import Base, create_session, trans
from datetime import datetime, timedelta
from time import localtime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Sequence
import sqlalchemy as sa

class Todo(Base):
    __tablename__ = 'todo'
    __table_args__ = {'useexisting': True}
    indx = Column('indx', Integer, Sequence('todo_indx_seq', optional=True), primary_key=True)
    name = Column('name', String(255), nullable=False)
    time = Column('time', DateTime)
    duration = Column('duration', Integer)
    warnsec = Column('warnsec', Integer)
    descr = Column('descr', Text, nullable=False)
    priority = Column('priority', Integer)

    def __init__(self, name, time, duration, warnsec, descr, priority):
        self.name = name
        self.time = time
        self.duration = duration
        self.warnsec = warnsec
        self.descr = descr
        self.priority = priority

## UPGRADE PART

def upgrade():
    rlog(10, 'quote', 'upgrading')
    teller = 0
    oldfile = datadir + os.sep + 'old' + os.sep + 'todo'
    dbdir = datadir + os.sep + 'db' + os.sep + 'todo.db' 
    if os.path.exists(dbdir):
        try:
            from gozerbot.database.db import Db
            db = Db(dbtype='sqlite')
            db.connect('db/todo.db')
            result = db.execute(""" SELECT * FROM todo """)
            if result:
                for i in result:
                    todo.add(i[1], i[5],*i[2:4])
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
        for name, itemlist in oldpersist.data.iteritems():
            for item in itemlist:
                todo.add(name, item.descr, datetime.fromtimestamp(item.time), item.duration, \
item.warnsec, item.priority)
                teller += 1  
    except IOError, ex:
        if 'No such file' in str(ex):
            rlog(10, 'todo', 'nothing to upgrade')
    except Exception, ex:
        rlog(10, 'todo', "can't upgrade .. reason: %s" % str(ex))
        handle_exception()
    else:
        rlog(10, 'quote', "upgraded %s items" % teller)

## END UPGRADE PART

plughelp.add('todo', 'todo lists')

todolock = thread.allocate_lock()
locked = lockdec(todolock)

class TodoDb(object):

    """ database todo interface """

    @trans
    def reset(self, session, name): 
        item = session.query(Todo).filter(Todo.name==name.lower).first()
        session.delete(item)
        return 1

    def size(self):
        """ return number of todo's """
        s = create_session()
        count = s.query(sa.func.count(Todo.indx)).first()[0]
        return count 
        
    def get(self, name):
        """ get todo list of <name> """
        s = create_session()
        name = name.lower()
        result = s.query(Todo).filter(Todo.name==name).order_by(Todo.priority.desc()).all()
        return result

    def getid(self, idnr):
        """ get todo data of <idnr> """
        s = create_session()
        result = s.query(Todo).filter(Todo.indx==idnr).first()
        return result

    @trans
    def setprio(self, session, who, todonr, prio):
        """ set priority of todonr """
        item = session.query(Todo).filter(Todo.indx==todonr).first()
        if item:
            item.priority = prio
            session.commit()
            return 1

    def getprio(self, todonr):
        """ get priority of todonr """
        s = create_session()
        result =  s.query(Todo).filter(Todo.indx==todonr).first()
        if result:
            return result.priority

    def getwarnsec(self, todonr):
        """ get priority of todonr """
        s = create_session()
        result =  s.query(Todo).filter(Todo.indx==todonr).first()
        return result

    @trans
    def settime(self, session, who, todonr, ttime):
        """ set time of todonr """
        item = session.query(Todo).filter(Todo.indx==todonr).first()
        if item:
            item.time = datetime.fromtimestamp(ttime)
            session.refresh(item)
            return 1
    @trans
    def add(self, session, name, txt, ttime=0, duration=0, warnsec=0, priority=0, alarmnr=None):
        """ add a todo """
        name = name.lower()
        txt = txt.strip()
        if not ttime:
            if config['dbtype'] == 'mysql':
                todo = Todo(name, 0, duration, warnsec, txt, priority)
            else:
                todo = Todo(name, datetime.min, duration, warnsec, txt, priority)
            session.save(todo)
        else:
            todo = Todo(name, datetime.fromtimestamp(ttime), duration, warnsec, txt, priority)
            session.save(todo)
        session.commit()
        return todo.indx

    @trans
    def delete(self, session, name, indexnr):
        """ delete todo item """
        name = name.lower()
        try:
            warnsec = self.getwarnsec(indexnr)[0][0]
            if warnsec:
                alarmnr = 0 - warnsec
                if alarmnr > 0:
                    alarms.delete(alarmnr)
        except (IndexError, TypeError):
            pass
        item = session.query(Todo).filter(Todo.name==name and Todo.indx==indexnr).first()
        if item:
            session.delete(item)
            return 1

    def toolate(self, name):
        """ show if there are any time related todoos that are too late """
        s = create_session()
        items = s.query(Todo).filter(Todo.name==name.lower and Todo.time<datetime.now()).all()
        return items

    def withintime(self, name, time1, time2):
        """ show todo list within time frame """
        name = name.lower()
        s = create_session()
        items = s.query(Todo).filter(Todo.name==name.lower and Todo.time>datetime.fromtimestamp(time1) and Todo.time<datetime.fromtimestamp(time2)).all()
        return items

    def timetodo(self, name):
        s = create_session()
        name = name.lower()
        if 'mysql' in config['dbtype']:
            items = s.query(Todo).filter(Todo.name==name.lower).filter(Todo.time>0).all()
        else:
            items = s.query(Todo).filter(Todo.name==name.lower).filter(Todo.time>datetime.min).all()
        return items

todo = TodoDb()
Base.metadata.create_all()
assert(todo)

def size():
    """ return number of todo entries """
    return todo.size()

def handle_todoupgrade(bot, ievent):
    if todo.size():
         if '-f' in ievent.optionset:
             pass
         else:
             ievent.reply('there are already todo items in the main database .. not upgrading')
             ievent.reply('use the -f option to force an upgrade')
             return
    ievent.reply('upgrading todo')
    nritems = upgrade()
    ievent.reply('%s items upgraded' % nritems)

cmnds.add('todo-upgrade', handle_todoupgrade, 'OPER', options={'-f': ''})



def handle_todo(bot, ievent):
    """ todo [<item>] .. show todo's or set todo item .. a time/date can be \
given"""
    if len(ievent.args) > 0:
        handle_todo2(bot, ievent)
        return
    name = users.getname(ievent.userhost)
    try:
        todoos = todo.get(name)
    except KeyError:
        ievent.reply('i dont have todo info for %s' % user.name)
        return
    saytodo(bot, ievent, todoos)

def handle_todo2(bot, ievent):
    """ set todo item """
    if not ievent.rest:
        ievent.missing("<what>")
        return
    else:
        what = ievent.rest
    name = users.getname(ievent.userhost)
    ttime = strtotime(what)
    nr = 0
    if not ttime == None:
        ievent.reply('time detected ' + time.ctime(ttime))
        what = striptime(what)
        alarmnr = alarms.add(bot.name, ievent.nick, ttime, what)
        nr = todo.add(name, what, ttime, alarmnr=alarmnr)
    else:
        nr = todo.add(name, what)
    ievent.reply('todo item %s added' % nr)

cmnds.add('todo', handle_todo, 'USER')
examples.add('todo', 'todo [<item>] .. show todo items or add a todo item', \
'1) todo 2) todo program the bot 3) todo 22:00 sleep')
tests.add('todo program the bot').add('todo', 'program the bot')

def handle_tododone(bot, ievent):
    """ todo-done <listofnrs> .. remove todo items """
    if len(ievent.args) == 0:
        ievent.missing('<list of nrs>')
        return
    try:
        nrs = []
        for i in ievent.args:
            nrs.append(int(i))
    except ValueError:
        ievent.reply('%s is not an integer' % i)
        return
    name = users.getname(ievent.userhost)
    nrdone = 0
    failed = []
    for i in nrs:
        try:
            todo.delete(name, i)
            nrdone += 1
        except Exception, ex:
            failed.append(i)
            handle_exception()
    if failed:
        ievent.reply('failed to delete %s' % ' .. '.join(failed))
    if nrdone == 1:
        ievent.reply('%s item deleted' % nrdone)
    elif nrdone == 0:
        ievent.reply('no items deleted')
    else:
        ievent.reply('%s items deleted' % nrdone)

cmnds.add('todo-done', handle_tododone, 'USER')
examples.add('todo-done', 'todo-done <listofnrs> .. remove items from \
todo list', '1) todo-done 1 2) todo-done 3 5 8')
aliases.data['done'] = 'todo-done'
tests.add('todo program the bot', 'todo item (\d+) added').add('todo-done %s', '(\d+) item deleted')

def handle_chantodo(bot, ievent):
    """ todo-chan [<item>] .. show channel todo's or set todo item for \
channel"""
    if ievent.rest:
        handle_chantodo2(bot, ievent)
        return
    todoos = todo.get(ievent.channel)
    saytodo(bot, ievent, todoos)

def handle_chantodo2(bot, ievent):
    """ set todo item for channel"""
    what = ievent.rest
    ttime = strtotime(what)
    nr = 0
    if not ttime  == None:
        ievent.reply('time detected ' + time.ctime(ttime))
        result = '(%s) ' % ievent.nick + striptime(what)
        alarmnr = alarms.add(bot.name, ievent.channel, ttime, result)
        nr = todo.add(ievent.channel, result, ttime, alarmnr=alarmnr)
    else:
        result = '(%s) ' % ievent.nick + what
        nr = todo.add(ievent.channel, result, 0)
    ievent.reply('todo item %s added' % nr)

cmnds.add('todo-chan', handle_chantodo, 'USER')
examples.add('todo-chan', 'todo-chan [<item>] .. add channel todo', \
'todo-chan fix bla')
aliases.data['chantodo'] = 'todo-chan'
tests.add('todo-chan program the bot').add('todo-chan', 'program the bot')

def handle_todochandone(bot, ievent):
    """ todo-chandone <listofnrs> .. remove channel todo item """
    if not ievent.rest:
        ievent.missing('<list of nrs>')
        return
    data = ievent.rest.split()
    try:
        nrs = []
        for i in data:
            nrs.append(int(i))
    except ValueError:
        ievent.reply('%s is not an integer' % i)
        return
    nrdone = 0
    failed = []
    for i in nrs:
        try:
            if todo.delete(ievent.channel, i):
                nrdone += 1
        except Excpetion, ex:
            failed.append(i)
            handle_exception()
    if failed:
        ievent.reply('failed to delete %s' % ' .. '.join(failed))
    if nrdone == 1:
        ievent.reply('%s item deleted' % nrdone)
    elif nrdone == 0:
        ievent.reply('no items deleted')
    else:
        ievent.reply('%s items deleted' % nrdone)

cmnds.add('todo-chandone', handle_todochandone, 'USER')
examples.add('todo-chandone', 'todo-chandone <listofnrs> .. remove item \
from channel todo list', 'todo-chandone 2')
aliases.data['chandone'] = 'todo-chandone'
tests.add('todo-chan program the bot', 'todo item (\d+) added').add('todo-chandone %s', '(\d+) item deleted')

def handle_settodo(bot, ievent):
    """ todo-set <name> <txt> .. add a todo to another user's todo list"""
    try:
        who = ievent.args[0]
        what = ' '.join(ievent.args[1:])
    except IndexError:
        ievent.missing('<nick> <what>')
        return
    if not what:
        ievent.missing('<nick> <what>')
        return
    userhost = getwho(bot, who)
    if not userhost:
        ievent.reply("can't find userhost for %s" % who)
        return
    whouser = users.getname(userhost)
    if not whouser:
        ievent.reply("can't find user for %s" % userhost)
        return
    name = users.getname(ievent.userhost)
    if not users.permitted(userhost, name, 'todo'):
        ievent.reply("%s doesn't permit todo sharing for %s " % \
(who, name))
        return
    what = "%s: %s" % (ievent.nick, what)
    ttime = strtotime(what)
    nr = 0
    if not ttime  == None:
        ievent.reply('time detected ' + time.ctime(ttime))
        what = striptime(what)
        alarmnr = alarms.add(bot.name, who, ttime, what)
        nr = todo.add(whouser, what, ttime, alarmnr=alarmnr)
    else:
        nr = todo.add(whouser, what, 0)
    ievent.reply('todo item %s added' % nr)

cmnds.add('todo-set', handle_settodo, 'USER')
examples.add('todo-set', 'todo-set <nick> <txt> .. set todo item of \
<nick>', 'todo-set dunker bot proggen')
tests.add('user-addpermit owner todo').add('todo-set {{ me }} program the bot', 'todo item (\d+) added')

def handle_gettodo(bot, ievent):
    """ todo-get <nick> .. get todo of another user """
    try:
        who = ievent.args[0]
    except IndexError:
        ievent.missing('<nick>')
        return
    userhost = getwho(bot, who)
    if not userhost:
        ievent.reply("can't find userhost for %s" % who)
        return
    whouser = users.getname(userhost)
    if not whouser:
        ievent.reply("can't find user for %s" % userhost)
        return
    name = users.getname(ievent.userhost)
    if not users.permitted(userhost, name, 'todo'):
        ievent.reply("%s doesn't permit todo sharing for %s " % (who, name))
        return
    todoos = todo.get(whouser)
    saytodo(bot, ievent, todoos)

cmnds.add('todo-get', handle_gettodo, ['USER', 'WEB'])
examples.add('todo-get', 'todo-get <nick> .. get the todo list of \
<nick>', 'todo-get dunker')
tests.add('todo program the bot').add('todo-get {{ me }}', 'program the bot')

def handle_todotime(bot, ievent):
    """ todo-time .. show time related todoos """
    name = users.getname(ievent.userhost)
    todoos = todo.timetodo(name)
    saytodo(bot, ievent, todoos)

cmnds.add('todo-time', handle_todotime, 'USER')
examples.add('todo-time', 'todo-time .. show todo items with time fields', \
'todo-time')
aliases.data['tt'] = 'todo-time'
tests.add('todo 11-11-2011 test', 'time detected').add('todo-time', 'test')

def handle_todoweek(bot, ievent):
    """ todo-week .. show time related todo items for this week """
    name = users.getname(ievent.userhost)
    todoos = todo.withintime(name, today(), today()+7*24*60*60)
    saytodo(bot, ievent, todoos)

cmnds.add('todo-week', handle_todoweek, 'USER')
examples.add('todo-week', 'todo-week .. todo items for this week', 'todo-week')
tests.add('tomorrow test the bot').add('todo-week', 'test the bot')

def handle_today(bot, ievent):
    """ todo-today .. show time related todo items for today """
    name = users.getname(ievent.userhost)
    todoos = todo.withintime(name, today(), today()+24*60*60)
    saytodo(bot, ievent, todoos)

cmnds.add('todo-today', handle_today, 'USER')
examples.add('todo-today', 'todo-today .. todo items for today', 'todo-today')
aliases.data['today'] = 'todo-today'
tests.add('todo test the bot').add('todo-today', 'test the bot')

def handle_tomorrow(bot, ievent):
    """ todo-tomorrow .. show time related todo items for tomorrow """
    username = users.getname(ievent.userhost)
    if ievent.rest:
        what = ievent.rest
        ttime = strtotime(what)
        if ttime != None:
            if ttime < today() or ttime > today() + 24*60*60:
                ievent.reply("%s is not tomorrow" % \
time.ctime(ttime + 24*60*60))
                return
            ttime += 24*60*60
            ievent.reply('time detected ' + time.ctime(ttime))
            what = striptime(what)
        else:
            ttime = today() + 42*60*60
        todo.add(username, what, ttime)   
        ievent.reply('todo added')    
        return
    todoos = todo.withintime(username, today()+24*60*60, today()+2*24*60*60)
    saytodo(bot, ievent, todoos)

cmnds.add('todo-tomorrow', handle_tomorrow, 'USER')
examples.add('todo-tomorrow', 'todo-tomorrow .. todo items for tomorrow', \
'todo-tomorrow')
aliases.data['tomorrow'] = 'todo-tomorrow'
tests.add('todo-tomorrow test the bot').add('todo-time', 'test the bot')

def handle_setpriority(bot, ievent):
    """ todo-setprio [<channel|name>] <itemnr> <prio> .. show priority \
        on todo item """
    try:
        (who, itemnr, prio) = ievent.args
    except ValueError:
        try:
            (itemnr, prio) = ievent.args
            who = users.getname(ievent.userhost)
        except ValueError:
            ievent.missing('[<channe|namel>] <itemnr> <priority>')
            return
    try:
        itemnr = int(itemnr)
        prio = int(prio)
    except ValueError:
        ievent.missing('[<channel|name>] <itemnr> <priority>')
        return
    who = who.lower()
    todo.setprio(who, itemnr, prio)
    ievent.reply('priority set')

cmnds.add('todo-setprio', handle_setpriority, 'USER')
examples.add('todo-setprio', 'todo-setprio [<channel|name>] <itemnr> <prio> \
.. set todo priority', '1) todo-setprio #dunkbots 2 5 2) todo-setprio owner \
3 10 3) todo-setprio 2 10')
aliases.data['setprio'] = 'todo-setprio'
tests.add('todo test the bot', 'todo item (\d+) added').add('todo-setprio %s 10', 'priority set')

def handle_todosettime(bot, ievent):
    """ todo-settime [<channel|name>] <itemnr> <timestring> .. set time \
        on todo item """
    ttime = strtotime(ievent.txt)
    if ttime == None:
        ievent.reply("can't detect time")
        return   
    txt = striptime(ievent.txt)
    try:
        (who, itemnr) = txt.split()
    except ValueError:
        try:
            (itemnr, ) = txt.split()
            who = users.getname(ievent.userhost)
        except ValueError:
            ievent.missing('[<channe|namel>] <itemnr> <timestring>')
            return
    try:
        itemnr = int(itemnr)
    except ValueError:
        ievent.missing('[<channel|name>] <itemnr> <timestring>')
        return
    who = who.lower()
    if not todo.settime(who, itemnr, ttime):
        ievent.reply('no todo %s found for %s' % (itemnr, who))
        return
    ievent.reply('time of todo %s set to %s' % (itemnr, time.ctime(ttime)))

cmnds.add('todo-settime', handle_todosettime, 'USER')
examples.add('todo-settime', 'todo-settime [<channel|name>] <itemnr> \
<timestring> .. set todo time', '1) todo-settime #dunkbots 2 13:00 2) \
todo-settime owner 3 2-2-2010 3) todo-settime 2 22:00')
tests.add('todo test the bot', 'todo item (\d+) added').add('todo-settime %s 11:00', 'time of todo %s set')

def handle_getpriority(bot, ievent):
    """ todo-getprio <[channel|name]> <itemnr> .. get priority of todo \
        item """
    try:
        (who, itemnr) = ievent.args
    except ValueError:
        try:
            itemnr = ievent.args[0]
            who = users.getname(ievent.userhost)
        except IndexError:
            ievent.missing('[<channel|name>] <itemnr>')
            return
    try:
        itemnr = int(itemnr)
    except ValueError:
        ievent.missing('[<channel|name>] <itemnr>')
        return
    who = who.lower()
    prio = todo.getprio(itemnr)
    ievent.reply('priority is %s' % prio)

cmnds.add('todo-getprio', handle_getpriority, 'USER')
examples.add('todo-getprio', 'todo-getprio [<channel|name>] <itemnr> .. get \
todo priority', '1) todo-getprio #dunkbots 5 2) todo-getprio 3')
aliases.data['prio'] = 'todo-getprio'
tests.add('todo test the bot', 'todo item (\d+) added').add('todo-getprio %s', 'priority is 0')

def saytodo(bot, ievent, todoos):
    """ output todo items of <name> """
    result = []
    now = datetime.now()
    if not todoos:
        ievent.reply('nothing todo ;]')
        return
    for i in todoos:
        res = ""
        res += "%s) " % i.indx
        if i.priority:
            res += "[%s] " % i.priority
        if i.time and not i.time == i.time.min:
            if i.time < now:
                res += 'TOO LATE: '
            res += "%s %s " % (i.time.ctime(), i.descr)
        else:
            res += "%s " % i.descr
        result.append(res.strip())
    if result:
        ievent.reply("todolist of %s: " % ievent.nick, result, nritems=True)
