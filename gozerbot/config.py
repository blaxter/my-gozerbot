# gozerbot/config.py
#
#

""" gozerbot config module. """

__copyright__ = 'this file is in the public domain'

# gozerobt imports
from utils.exception import handle_exception
from simplejson import loads, dumps

# basic imports
import os, types, thread, logging

# gozerbot version
version = "GOZERBOT 0.9.0.15 DEV"


class Config(dict):

    """ config class is a dict containing json strings. is writable to file 
        and human editable.
    """

    def __init__(self, ddir=None, filename=None, inittxt=None, *args, **kw):
        dict.__init__(self, *args, **kw)
        self.dir = ddir or 'gozerdata'
        self.filename = filename or 'config'
        self.cfile = self.dir + os.sep + self.filename

        #  check if provided dir exists if not create it
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)

        # see if initial data has to be written
        if inittxt and not os.path.exists(self.cfile):
            self.write_init(inittxt)

        self.configlist = []
        self.lock = thread.allocate_lock()
        self.load()

    def __getitem__(self, item):
        if not self.has_key(item):
            return None
        else:
            return dict.__getitem__(self, item)

    def set(self, item, value):
        dict.__setitem__(self, item, value)
        self.save()

    def load(self):

        """ load the config file. """

        self.reload()

        if self.filename == 'mainconfig':
            self['version'] = version
            if not self['loadlist']:
                self['loadlist'] = ["alias", "all", "at", "chanperm", "choice", "code", "core", "count", "fleet", "googletalk", "grep", "ignore", "irc", "jabber", "job", "misc", "nickcapture", "nickserv", "not", "quote", "reload", "rest", "reverse", "size", "sort", "tail", "tell", "to", "underauth", "uniq", "user", "userstate", "stats"]

    def save(self):

        """ save the config file. """

        written = []
        curitem = None

        try:

            self.lock.acquire()

            # read existing config file if available
            try:
                self.configlist = open(self.cfile, 'r').readlines()
            except IOError:
                self.configlist = []

            # make temp file
            configtmp = open(self.cfile + '.tmp', 'w')
            teller = 0

            # write header if not already there
            if not self.configlist:
                configtmp.write('# %s\n\n' % self.cfile)

            # loop over original lines replacing updated data
            for line in self.configlist:
                teller += 1

                # skip comment
                if line.startswith('#'):
                    configtmp.write(line)
                    continue

                # take part after the =
                try:
                    keyword = line.split('=')[0].strip()
                    curitem = keyword
                except IndexError:
                    configtmp.write(line)
                    continue

                # write JSON string of data
                if self.has_key(keyword):
                    configtmp.write('%s = %s\n' % (keyword, dumps(self[keyword])))
                    written.append(keyword)
                else:
                    configtmp.write(line)

            # write data not found in original config file
            for keyword, value in self.iteritems():
                if keyword in written:
                    continue
                curitem = keyword
                configtmp.write('%s = %s\n' % (keyword, dumps(value)))

            # move temp file to original
            configtmp.close()
            os.rename(self.cfile + '.tmp', self.cfile)
            self.lock.release()
            return teller

        except Exception, ex:
            print "ERROR WRITING %s CONFIG FILE: %s .. %s" % (self.cfile, str(ex), curitem)
            try:
                self.lock.release()
            except:
                pass
            return

    def reload(self):

        """ reload the config file. """

        curline = ""

        # read file and set config values to loaded JSON entries
        try:

            # open file
            f = open(self.cfile, 'r')

            # loop over data in config file            
            for line in f:
                curline = line
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                else:
                    key, value = line.split('=', 1)
                    self[key.strip()] = loads(unicode(value.strip()))

        except IOError:
            pass
        except Exception, ex:
            print "ERROR READING %s CONFIG FILE: %s .. %s" % (self.cfile, str(ex), curline)

    def write_init(self, txt):

        """ write initial version of the config file .. mainconfig or fleet
            config.
        """

        # check if datadir is there .. if not create it
        if not os.path.isdir(self.dir):
            os.mkdir(self.dir)

        # check if config file is already there .. if not init it 
        if not os.path.isfile(self.cfile):
            cfgfile = open(self.cfile, 'w')
            cfgfile.write(txt)
            cfgfile.close()


""" init txt for main config file. """


mainconfigtxt = """# gozerbot config
#
#
# TAKE NOTE THAT FORMAT IS IN JSON NOW SO USE " not '

# GLOBAL OWNER

# example: owner = ["~bart@127.0.0.1"] (include ident if needed)
owner = []

# logging level
loglevel = 10

# list of plugins to log
loglist = []

# quit message
quitmsg = "http://gozerbot.org"

# botterdata dir mask
mask = "700"

# enable debugging
debug = 0

# database stuff

nodb = 0
dbtype = "sqlite"
dbname = "db/main.db"
dbhost = "localhost"  
dbuser = "bart"
dbpasswd = "mekker2"

# json backstore

#jsonuser = "users.json"

# loadlist
loadlist = ["alias", "all", "at", "chanperm", "choice", "code", "core", "count", "fleet", "googletalk", "grep", "ignore", "irc", "jabber", "job", "misc", "nickcapture", "nickserv", "not", "quote", "reload", "rest", "reverse", "size", "sort", "tail", "tell", "to", "underauth", "uniq", "user", "userstate", "plug"]

"""


""" init txt for fleet config """


fleetbotconfigtxt = """# gozerbot fleet bot config
#
#
# TAKE NOTE THAT FORMAT IS IN JSON NOW SO USE " not '

## MAIN STUFF

# set to 0 to disable
enable = 1

# set type to jabber or irc
type = "irc"

# owner (irc/jabber)
owner = []

## CONNECTION STUFF

# user (jabber) .. needs to be full JID because server is taken from it
user = "botter@jabber.xs4all.nl"

# nick (irc)
nick = "gozerbot"

# server (irc)
server = "localhost"

# host (jabber) .. server to connect to
host = "jabber.xs4all.nl"

# password (irc and jabber)
password = ""

# port (irc and jabber) .. 0 uses default value
port = 0

# ssl (irc)
ssl = 0

# use ipv6 (irc)
ipv6 = 0

# bots username (irc)
username = "gozerbot"

# bots realname (irc)
realname = "GOZERBOT"

## OTHER STUFF

# default control character
defaultcc = "!"

# quit message
quitmsg = "http://gozerbot.org"

# bindhost .. uncomment to enable
bindhost = ""

# disable limiter (irc)
nolimiter = 0

# nickserv .. set pass to enable nickserv ident (irc)
nickservpass = ""
nickservtxt = ["set unfiltered on"]

# allow every command except OPER commands
auto_register = 0

# strip ident string
stripident = 0

loadlist = []

"""


# main config object
config = Config(filename='mainconfig', inittxt=mainconfigtxt)
