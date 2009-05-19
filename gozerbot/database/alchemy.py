# gozerbot/databse/alchemy.py
#
#

""" alchemy interface. """

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from gozerbot.stats import stats
from gozerbot.datadir import datadir
from gozerbot.config import config
from gozerbot.generic import rlog, lockdec
from gozerbot.utils.exception import handle_exception

# sqlalchemy imports
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy import Text, Integer, Sequence, ForeignKey, DateTime
from sqlalchemy import create_engine, Column, String, Table
from sqlalchemy.orm import  scoped_session, sessionmaker, relation, create_session

# basic imports
import sqlalchemy, thread, os, time, logging

# debug settings
if config['debug']:
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# locks
alchemylock = thread.allocate_lock()
dblocked = lockdec(alchemylock)

# vars
Base = declarative_base()
Session = None
engine = None

def geturi(ddir=None, mainconfig=None):

    """  determine database URI from config file """

    d = ddir or datadir

    # set config file
    if mainconfig:
        config = mainconfig 
    else:
        from gozerbot.config import config

    # if dburi not provided in config file construct it
    if not config['dburi']:

        if not 'sqlite' in config['dbtype'] and not 'mysql' in config['dbtype']:
            dburi = "%s://%s:%s@%s/%s" % (config['dbtype'], config['dbuser'], \
config['dbpasswd'], config['dbhost'], config['dbname'])
        elif 'mysql' in config['dbtype']:
            dburi = "%s://%s:%s@%s/%s?charset=utf8&use_unicode=0" % (config['dbtype'], config['dbuser'], \
config['dbpasswd'], config['dbhost'], config['dbname'])
        else:
            if not os.path.isdir(d + os.sep + 'db'):
                os.mkdir(d + os.sep + 'db')
            dburi = "sqlite:///%s/%s" % (ddir or datadir, config['dbname'])

    else:
        # dburi found in config
        dburi = config['dburi']

        # determine dbtype
        try:
            dbtype = dburi.split(':')[0]
        except:
            rlog(10, 'alchemy', "can't extract db data from dburi")
            dbtype = 'unknown'

        # save dbtype
        if config['dbtype'] != dbtype:
            config['dbtype'] = dbtype
            config.save()

    return dburi

def dbstart(ddir=None, mainconfig=None):

    """ start the database connection setting Session and engine. """

    dburi = geturi(ddir, mainconfig)

    # only show dburi if it doesn't contain a password
    if '///' in dburi:
        rlog(10, 'alchemy', 'starting database %s' % dburi)
    else:
        rlog(10, 'alchemy', 'starting database')

    # create engine
    if 'mysql' in config['dbtype']:
        engine = create_engine(dburi, strategy='threadlocal', pool_recycle=3600, max_overflow=-1)
    else:
        engine = create_engine(dburi, strategy='threadlocal')

    # setup metadata and session
    Base.metadata.bind = engine
    rlog(10, 'alchemy', 'checking for tables')
    Base.metadata.create_all()
    Session = scoped_session(sessionmaker(autocommit=True))
    Session.configure(bind=engine)
    stats.up('alchemy', 'engines')

    return (Session, engine)

def startmaindb(ddir=None, mainconfig=None):

    """ start the main database. """

    global Session
    global engine

    Session, engine = dbstart(ddir, mainconfig)

### MODEL

user = Table('user', Base.metadata,
    Column('name', String(255), primary_key=True)
)

email = Table('email', Base.metadata,
    Column('name', String(255), ForeignKey(user.c.name), nullable=False),
    Column('email', String(255), nullable=False),
    Column('order', Integer, nullable=False)
)

class User(Base):
    __table__ = user
    _userhosts = relation("UserHost", backref="user", cascade="all, delete-orphan")
    _perms = relation("Perms", backref="user", cascade="all, delete-orphan")
    _permits = relation("Permits", backref="user",cascade="all, delete-orphan" )
    _statuses = relation("Statuses", backref="user", cascade="all, delete-orphan")
    _pasword = relation("Passwords", backref="user", cascade="all, delete-orphan")
    _email = relation("Email", backref="user", collection_class=ordering_list('order'),
                        cascade="all, delete-orphan", order_by=[email.c.order])
    email = association_proxy('_email', 'email')
    userhosts = association_proxy('_userhosts', 'userhost')
    perms = association_proxy('_perms', 'perm')
    permits = association_proxy('_permits', 'permit')
    statuses = association_proxy('_statuses', 'status')
    password = association_proxy('_password', 'passwd')

class Email(Base):
    __table__ = email
    __mapper_args__ = {'primary_key':[email.c.name,email.c.email]}

    def __init__(self, email):
        self.email = email

class UserHost(Base):
    __tablename__ = 'userhosts'
    userhost = Column('userhost', String(255), primary_key=True)
    name = Column('name', String(255), ForeignKey('user.name'), nullable=False)

    def __init__(self, userhost):
        self.userhost = userhost

class Perms(Base):
    __tablename__ = 'perms'
    name = Column('name', String(255), ForeignKey('user.name'), nullable=False)
    perm = Column('perm', String(255), nullable=False)
    __mapper_args__ = {'primary_key':[name,perm]}

    def __init__(self, perm):
        self.perm = perm

class Permits(Base):
    __tablename__ = 'permits'
    name = Column('name', String(255), ForeignKey('user.name'), nullable=False)
    permit = Column('permit', String(255), nullable=False)
    __mapper_args__ = {'primary_key':[name,permit]}

    def __init__(self, permit):
        self.permit = permit

class Statuses(Base):    
    __tablename__ = 'statuses'
    name = Column('name', String(255), ForeignKey('user.name'), nullable=False)
    status = Column('status', String(255), nullable=False)
    __mapper_args__ = {'primary_key':[name,status]}

    def __init__(self, status):
        self.status = status

class Passwords(Base):    
    __tablename__ = 'passwords'
    name = Column('name', String(255), ForeignKey('user.name'), primary_key=True)
    passwd = Column('passwd', String(255), nullable=False)

    def __init__(self, passwd):
        self.passwd = passwd

### END MODEL

def create_session():

    """ create a session ready for use. """

    stats.up('alchemy', 'sessions')
    session = Session()
    return session

def query(q, session=None):

    """ do a query on the database. """

    stats.up('alchemy', 'query')
    if not session:
        session = create_session()
    res = session.query(q)
    return res

def getuser(userhost, session=None):

    """ get a user based on userhost. """

    stats.up('alchemy', 'getuser')

    if not session:
        session = create_session()

    try:
        user = query(UserHost, session).filter_by(userhost=userhost).first()
        if user:
            res = query(User, session).filter_by(name=user.name.lower()).first()
            if res: 
                return res
    except sqlalchemy.exc.TimeoutError:
        rlog(10, 'alchemy', 'timeout occured')
        session.rollback()
    except Exception, ex:
        session.rollback()
        raise

def byname(name , session=None):

    """ get a users based on name. """

    res = query(User, session).filter_by(name=name.lower()).first()
    return res

def trans(func, ismethod=True):

    """ transaction function attribute. """

    @dblocked
    def transaction(*args, **kwargs):

        """ the tranasction wrapper .. works on methods. """

        try:
            stats.up('alchemy', 'transactions')
            session = create_session()
            session.begin(subtransactions=True)
            arglist = list(args)
            if not ismethod:
                arglist.insert(0, session)
            else:
                arglist.insert(1, session)
            res = func(*arglist, **kwargs)
            session.flush()
            engine.commit()
        except sqlalchemy.exc.TimeoutError:
            rlog(10, 'alchemy', 'timeout occured')
            session.rollback()
        except Exception ,ex:
            session.rollback()
            raise

        return res

    return transaction

def transfunc(func):

    """ transaction wrapper for functions. """

    return trans(func, ismethod=False)

@transfunc
def dbupgrade(session, mainconfig=None):

    """ upgrade the database. """

    time.sleep(10)
    print 'upgrading users'
    users = session.query(UserHost).all()
    upgraded = []

    # populate the User table
    for user in users:
        name = user.name
        if name in upgraded:
            continue
        try:
            if not byname(name):
                newuser = User(name=name)
                session.add(newuser)
            upgraded.append(name)
        except sqlalchemy.exc.IntegrityError, ex:
            pass
        except:
            handle_exception()

    session.commit()
    print "upgraded: %s" % ' .. '.join(upgraded) 
    print 'upgrading email table'
    from gozerbot.database.db import Db

    # upgrade email table
    try:
        db = Db(config=mainconfig)
        if db.dbtype == 'mysql':
            db.execute("ALTER TABLE email ADD COLUMN email.order INT")
        else:
            db.execute("ALTER TABLE email ADD COLUMN 'order' INT")
    except Exception, ex:
        if 'already exists' in str(ex) or 'duplicate column name' in \
str(ex).lower():
            pass
        else:
            handle_exception()
