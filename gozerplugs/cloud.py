# gozerplugs/cloud.py
# 
#

__copyright__ = 'this file is in the public domain'
__gendocfirst__ = ['cloud-enable', 'cloud-startserver', 'cloud-boot', \
'cloud-joinall']
__gendoclast__ = ['cloud-stopserver', 'cloud-disable']

from gozerbot.generic import handle_exception, rlog, getpostdata, waitforqueue
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
from gozerbot.threads.threadloop import ThreadLoop
from gozerbot.rest.server import RestServerAsync, RestRequestHandler
from gozerbot.rest.client import RestClientAsync
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.plugins import plugins
from gozerbot.users import users
from gozerbot.threads.thr import start_new_thread
from gozerbot.fleet import fleet
from gozerbot.irc.ircevent import Ircevent
from gozerbot.aliases import aliasset
from gozerbot.persist.persiststate import PersistState
from gozerbot.datadir import datadir
from gozerbot.persist.pdod import Pdod
from simplejson import dumps
import socket, re, asyncore, time, random, Queue, os

plughelp.add('cloud', 'cloud network')

## UPGRADE PART

def upgrade():
    pass

##33 END UPGRADE PART

cfg = PersistConfig()
cfg.define('enable', 0)
cfg.define('wait', 5)
cfg.define('host' , socket.gethostbyname(socket.getfqdn()))
cfg.define('name' , socket.getfqdn())
cfg.define('port' , 10101)
cfg.define('disable', [])
cfg.define('booturl', 'http://gozerbot.org:10101/')
cfg.define('servermode', 0)

waitre = re.compile(' wait (\d+)', re.I)
hp = "%s:%s" % (cfg.get('host'), cfg.get('port'))
url = "http://%s" % hp

# CLIENT PART

class Client(RestClientAsync):

    def auth(self, userhost, perm):
        kwargs = {}
        kwargs['userhost'] = userhost
        kwargs['perm'] = perm
        self.sendpost(kwargs)

class Node(object):

    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.client = Client(name, url)
        self.seen = time.time()
        self.synced = time.time()
        self.regtime = time.time()
        self.filter = []
        self.catch = []
        self.lasterrortime = None
        self.lasterror = ""
        self.insocket = None

    def __str__(self):
        return "name=%s url=<%s> seen=%s" % (self.name, self.url, self.regtime)

    def doget(self, mount, cb, *args, **kwargs):
        self.client = Client(self.url + mount, self.name).addcb(cb)
        self.client.get()
        return self.client

    def dopost(self, mount, cb, *args, **kwargs):
        self.client = Client(self.url + mount, self.name).addcb(cb)
        self.client.post(**kwargs)
        return self.client

    def ping(self, cb):
        self.doget('/gozernet/ping', cb) 

class Cloud(ThreadLoop):

    def __init__(self):
        ThreadLoop.__init__(self, 'cloud')
        self.datadir = datadir + os.sep + 'plugs' + os.sep + 'cloud'
        self.nodes = {}
        self.state = Pdod(self.datadir + os.sep + 'state')
        self.startup = Pdod(self.datadir + os.sep + 'startup')
        if not self.state.has_key('ignore'):
            self.state['ignore'] = []
        if not self.state.has_key('names'):
            self.state['names'] = {}
        if not self.startup.has_key('start'):
            self.startup['start'] = {}
        self.enabled = False
        self.running = False

    def addifping(self, name, url):
        if not url.endswith('/'):
            url += '/'
        node = Node(name, url)
        def cb(client, result):
            if result.error:
                rlog(0, url, 'failed to receive pong .. not adding: %s' % \
result.error)
                return    
            if 'pong' in result.data:
                self.add(name, url)
            else:
                rlog(0, url, 'invalid ping data')
        client = Client(url + 'gozernet/ping').addcb(cb)
        client.get()

    def add(self, name, url, persist=True):
        if not url.endswith('/'):
            url += '/'
        node = Node(name, url)
        self.nodes[url] = node 
        self.state.set('names', name,  url)
        if persist:
            self.persist(name, url)
        rlog(0, url, 'added %s node <%s>' % (name, url))
        return self.nodes[url]

    def start(self, regname, regport, booturl=None):
        ThreadLoop.start(self)
        self.enabled = True
        for name, url in self.startup['start'].iteritems():
            self.add(name, url)
        def cb(client, result):
            if result.error:
                rlog(10, booturl, 'boot error: %s' % result.error)
            else:
                rlog(10, booturl, 'boot result: %s' % result.data)
        self.boot(regname, regport, booturl, cbin=cb)

    def handle(self, *args):
        asyncore.loop()

    def persist(self, name, url):
        try:
            if self.startup['start'][name] == url:
                return
        except KeyError:
            pass
        self.startup.set('start', name, url)
        self.startup.save()

    def get(self, url):
        return self.nodes[url]

    def byname(self, name):
        try:
            url = self.state['names'][name]
            if url:
                return self.get(url)
        except KeyError:
            return None

    def remove(self, id):
        target = self.get(id)
        if not target:
            return
        del self.state['names'][target.name]
        del self.nodes[id]

    def unpersist(self, url):
        try:
            del self.startup['start'][url]
            self.startup.save()
        except KeyError:
            pass
            
    def ignore(self, url):
        self.state['ignore'].append(url)

    def unignore(self, url):
        self.state.data['ignore'].remove(url)
        self.state.save()

    def doget(self, mount, *args, **kwargs):
        self.put('go')
        for url, node in self.nodes.iteritems():
            node.doget(mount, *args, **kwargs)

    def dopost(self, mount, *args, **kwargs):
        self.put('go')
        for url, node in self.nodes.iteritems():
            node.dopost(mount, *args, **kwargs)

    def getnodes(self):
        result = []
        for url, node in self.nodes.iteritems():
            result.append((node.name, url))
        return result

    def getname(self, url):
        return self.get(url).name

    def addrecord(self, regname, url, cbin=None):
        rlog(0, regname, 'sending addrecord request')
        def cb(client, result):
            if result.error:
                rlog(10, url, 'addrecord error: %s' % result.error)
            else:
                rlog(10, url, 'record added')
        client = Client(url + '/gozernet/+addrecord').addcb(cb)
        if cbin:
            client.addcb(cbin)
        client.post(name=regname)
        return client

    def join(self, regname, regport, url, cbin=None):
        rlog(0, regname, 'joining on port %s' % regport)
        def cb(client, result):
            if result.error:
                rlog(0, url, 'join error: %s' % result.error)
            else:
                rlog(0, url, 'joined')
        client = Client(url + '/gozernet/+join').addcb(cb)
        if cbin:
            client.addcb(cbin)
        client.post(name=regname, port=regport)
        self.addrecord(regname, url, cbin)
        return client

    def joinall(self, regname, regport, cbin=None):
        for url, node in self.nodes.iteritems():
            self.join(regname, regport, url, cbin)
 
    def boot(self, regname, regport, url=None, cbin=None):
        rlog(10, 'cloud', 'booting')
        if url:
            self.sync(url, cbin)
        else:
            self.sync('http://gozerbot.org:10101', cbin)

    def fullboot(self, cbin=None):
        teller = 0
        threads = []
        for node in self.nodes.values():
            self.sync(node.url, False, cbin)
            teller += 1
        return teller

    def sync(self, url, throw=True, cbin=None):
        """ sync cache with node """
        def cb(client, result):
            if result.error:
                rlog(10, url, "can't sync: %s" % result.error)
                return
            for node in result.data:
                gnode = self.add(node[0], node[1])
                gnode.synced = time.time()
        client = Client('%s/gozernet/nodes/' % url).addcb(cb)
        if cbin:
            client.addcb(cbin)
        client.get()

    def size(self):
        return len(self.nodes)

    def list(self):
        res = []
        for node in self.nodes.values():
            res.append(str(node))
        return res

    def names(self): 
        return self.state['names'].keys()

# SERVER PART

def nodes_GET(server, request):
    return dumps(cloud.getnodes())

def ping_GET(server, request):
    return dumps('pong')

def addrecord_POST(server, request):
    try:
        input = getpostdata(request)
        name = input['name']
    except KeyError:
        rlog(5, host, 'addrecord .. no name provided')
        return dumps('no name provided')
    rlog(10, 'cloud', 'addrecord request for %s (%s)' % (name, request.ip)) 
    try:
        if not users.exist(name):
            users.add(name, ["cloud@%s" % request.ip, ], ['CLOUD', ])
            return dumps("%s added" % name)
    except Exception, ex:
        pass

def join_POST(server, request):
    try:
        (host, port) = request.client_address
    except:
        return dumps("can't determine host/port")
    try:
        input = getpostdata(request)
        port = input['port']
        name = input['name']
    except KeyError:
        rlog(0, host, 'join: no port number or name provided')
        return dumps('no port number/name provided')
    rlog(0, 'cloud', 'join request for %s %s' % (name, port))
    #if cloud.byname(name):
    #    rlog(10, host, '%s name already taken' % name)
    #    return dumps('node name already taken')
    hp = "%s:%s" % (host, port)
    url = 'http://%s/' % hp
    cloud.addifping(name, url)
    cloud.addrecord(cfg.get('name'), url)
    return dumps('node added')

def auth_POST(server, request):
    try:
        input = getpostdata(request)
        userhost = input['userhost']
        perm = input['perm']
    except KeyError:
        rlog(0, request.host, 'auth: no port number or name provided')
        return dumps('no port userhost/permission provided')
    return dumps(users.allowed(userhost, perm))

def dispatch_POST(server, request):
    """ dispatch request into the cloud """
    try:
        (host, port) = request.client_address
    except:
        return ["can't determine host/port", ]
    try:
        input = getpostdata(request)
        cmnd = input['cmnd']
    except KeyError:
        return dumps(['need cmnd value', ])
    try:
        channel = input['channel']
    except KeyError:
        channel = "#cloud"
    if not channel:
        channel = '#cloud'
    bot = fleet.getfirstbot()
    ievent = Ircevent()
    ievent.txt = cmnd  
    ievent.nick = 'cloud'
    ievent.userhost = "cloud@%s" % host
    ievent.channel = channel
    q = Queue.Queue()
    ievent.queues.append(q)
    ievent.speed = 3
    ievent.bot = bot
    result = []
    if plugins.woulddispatch(bot, ievent):
        start_new_thread(plugins.trydispatch, (bot, ievent))
    else:
        return dumps(["can't dispatch %s" % cmnd, ])
    result = waitforqueue(q, 10)
    if not result:
        return dumps(["no result", ])
    res = []
    for item in result:
        res.append(str(item))
    return dumps(res)

# AGGREGATOR PART

class Aggregator(ThreadLoop):

    def __init__(self):
        ThreadLoop.__init__(self, 'aggregator')
        self.results = {}
        self.outre = re.compile('(/S+)\:s(/S)+s')

    def handle(self, id, client, cmnd, result):
        if not self.results.has_key(id):
            self.results[id] = []
        self.results[id].append((client, cmnd, result))

    def get(self, id):
        try:
            result = self.results[id]
        except KeyError:
            return
        del self.results[id]
        return result

    def output(self, id, ievent):
        res = self.get(id)
        if res:
            out = []
            for r in res:
                client, cmnd, result = r
                if result.data:
                    if result.data not in out:
                        out.append(result.data)
            ievent.reply(out, dot=True, fromm=client.name)

    def aggregate(self, id, ievent):
        res = self.get(id)
        if res:
            agg = {}
            for r in res:
                client, cmnd, result = r
                if result.data:  
                    for item in result.data:
                       try:
                           name, nr = item.split()
                           if not agg.has_key(name):
                               agg[name] = int(nr)  
                           else:
                               agg[name] += int(nr)
                       except ValueError:
                           pass
            ievent.reply('results => ', agg)

# INIT ? SHUTDOWN PART / GLOBAL VARS

aggregator = None
server = None
cloud = None

def startcloud():
    global cloud
    try:
        cloud = Cloud()
        cloud.start(cfg.get('name'), cfg.get('port'), cfg.get('booturl'))
        aggregator.start()
        cloud.joinall(cfg.get('name'), cfg.get('port'))
        cloud.add(cfg.get('name'), url)
        rlog(10, 'cloud', 'total of %s nodes' % cloud.size())
        return cloud
    except Exception, ex:
        handle_exception()

def stopcloud():
    cloud and cloud.stop()
    aggregator and aggregator.stop()

def startserver():
    global server
    try:
        server = RestServerAsync((cfg.get('host'), cfg.get('port')), \
RestRequestHandler)
        if server:
            server.start()
            rlog(10, 'cloud', 'running at %s:%s' % (cfg.get('host'), cfg.get('port')))
            server.addhandler('/gozernet/nodes/', 'GET', nodes_GET)
            server.addhandler('/gozernet/ping/', 'GET', ping_GET)
            server.addhandler('/gozernet/+auth/', 'POST', auth_POST)
            server.addhandler('/gozernet/+join/', 'POST', join_POST)
            server.addhandler('/gozernet/+dispatch/', 'POST', dispatch_POST)
            server.addhandler('/gozernet/+addrecord/', 'POST', addrecord_POST)
            for mount in cfg.get('disable'):
                server.disable(mount)
    except socket.error, ex:
        rlog(10, 'cloud', str(ex))
    except Exception, ex:
        handle_exception()

def stopserver():
    try:
        if not server:
            rlog(10, 'cloud', 'server is already stopped')
            return
        server.stop = True
        server.server_close()
        time.sleep(3)
    except Exception, ex:
        handle_exception()
        pass


def init():
    """ init the 
cloud plugin """
    if not cfg.get('enable'):
        return 1
    global aggregator
    aggregator = Aggregator()
    if cfg.get('servermode'):
        startserver()
        time.sleep(3)
    startcloud()

def shutdown():
    """ shutdown the cloud plugin """
    try:
        stopcloud()
        stopserver()
    except Exception, ex:
        handle_exception()

def size():
    """ return number of cloud nodes """
    return cloud.size()

# CLOUD COMMANDS

def handle_clouddispatch(bot, ievent):
    """ dispatch <cmnd> on nodes """ 
    if not cfg.get('enable'):    
        ievent.reply('cloud is not enabled')
        return
    if not ievent.rest:
        ievent.missing('[--node <nodename>] [-d] [-e] <command>')
        return
    starttime = time.time()
    try:
        name = ievent.options['--node']
    except KeyError: 
        name = None  
    try:
        wait = int(ievent.options['--w'])
    except KeyError: 
        wait = 3
    except ValueError:
        ievent.reply("%s is not an integer" % ievent.options['--w'])
        return
    cmnd = ievent.rest
    id = ievent.nick + str(random.random())
    def cb(client, result):
        if result.error:   
            if '-e' in ievent.optionset:
                ievent.reply("%s: %s => %s" % (client.name, cmnd, result.error))
            return
        if '-d' in ievent.optionset:
            ievent.reply("%s: %s => " % (client.name, cmnd), result.data, dot=True)
        else:
            aggregator.put(id, client, cmnd, result)
    if name:
        node = cloud.byname(name)
        if not node:
            ievent.reply('there is no node named %s' % name)
            return
        ievent.reply('dispatching "%s" onto %s node - wait (%s)' % (cmnd, name, \
wait))
        node.dopost('gozernet/+dispatch', cb, cmnd=cmnd, channel=ievent.channel)
    else:
        ievent.reply('dispatching "%s" onto %s nodes - wait (%s)' % (cmnd, \
cloud.size(), wait))
        cloud.dopost('gozernet/+dispatch', cb, cmnd=cmnd, channel=ievent.channel)
    if '-d' in ievent.optionset:
        return
    time.sleep(wait)
    aggregator.output(id, ievent)

cmnds.add('dispatch', handle_clouddispatch, ['USER', ], allowqueue=False, \
threaded=True, options={'--node': '', '-e': '', '--w': '4', '-d': ''})
examples.add('dispatch', 'dispatch [-d] [-e] [--w <seconds to wait>] \
[--node <nodename>] <cmnd> .. execute <cmnd> in the cloud', \
'1) dispatch version 2) dispatch -d version 3) dispatch -e version 4) \
dispatch --w 10 version')
aliasset('d', 'dispatch')
aliasset('dd', 'dispatch -d')

def handle_cloudping(bot, ievent):
    """ do a ping on a cloud node """
    if not cfg.get('enable'):
        ievent.reply('cloud is not enabled .. see cloud-enable')
        return
    try:
        name = ievent.args[0]
    except IndexError:
        ievent.missing('<name>')
        return
    node = cloud.byname(name)
    if not node:
        ievent.reply('there is not node named %s' % name)
        return
    def cb(client, result):
        if result.error:
            ievent.reply('%s is not alive: %s' % (name, result.error))
            return
        if 'pong' in result.data:
            ievent.reply('%s is alive' % name)
    node.ping(cb)
    ievent.closequeue = False

cmnds.add('cloud-ping', handle_cloudping, 'OPER', threaded=True)
examples.add('cloud-ping', 'ping a cloud node', 'cloud-ping gozerbot.org')

def handle_cloudlist(bot, ievent):
    """ cloud-list .. list all nodes in cache """
    if not cfg.get('enable'):
        ievent.reply('cloud is not enabled')
        return
    ievent.reply("cloud nodes: ", cloud.list(), dot=' \002||\002 ')

cmnds.add('cloud-list', handle_cloudlist, 'OPER')
examples.add('cloud-list', 'list nodes cache', 'cloud-list')

def handle_cloudenable(bot, ievent):
    """ cloud-enable .. enable the cloud """
    ievent.reply('enabling the cloud')
    cfg.set('enable', 1)
    cfg.save()
    plugins.reload('gozerplugs', 'cloud')
    ievent.reply('done')

cmnds.add('cloud-enable', handle_cloudenable, 'OPER', threaded=True)
examples.add('cloud-enable', 'enable the gozerbot cloud', 'cloud-enable')

def handle_clouddisable(bot, ievent):
    """cloud-disable .. disable the gozerbot cloud """
    cfg.set('enable', 0)
    cfg.save()
    plugins.reload('gozerplugs', 'cloud')
    ievent.reply('cloud disabled')

cmnds.add('cloud-disable', handle_clouddisable, 'OPER', threaded=True)
examples.add('cloud-disable', 'disable the gozerbot cloud', 'cloud-disable')

def handle_cloudsync(bot, ievent):
    """ cloud-sync <node> .. sync nodes cache with node """ 
    if not cfg.get('enable'):
        ievent.reply('cloud is not enabled')
        return
    try:
        url = ievent.args[0]
    except IndexError:
        ievent.missing('<url>')
        return
    start = time.time()
    teller = 0
    def cb(client, result):
        for node in cloud.nodes.values():
            if node.synced > start:
                teller += 1
        ievent.reply('%s nodes synced' % str(teller))
    cloud.sync(url, cbin=cb)
    
cmnds.add('cloud-sync', handle_cloudsync, 'OPER', threaded=True)
examples.add('cloud-sync', 'cloud-sync <url> .. sync with provided node', \
'cloud-sync http://gozerbot.org:10101')

def handle_cloudaddnode(bot, ievent):
    """ cloud-addnode <name> <url> .. add node to cache """
    if not cfg.get('enable'):
        ievent.reply('cloud is not enabled')
        return
    try:
        (name, url) = ievent.args
    except ValueError:
        ievent.missing('<name> <url>')
        return
    client = Client(url)
    ip = socket.gethostbyname(client.host)
    url = "http://%s:%s" % (ip, client.port)
    cloud.add(name, url)
    cloud.persist(name, url)
    ievent.reply('%s added' % name)

cmnds.add('cloud-add', handle_cloudaddnode, 'OPER')
examples.add('cloud-add', 'cloud-add <name> <url> .. add a node to cache and \
persist it', 'cloud-add gozerbot.org http://gozerbot.org:10101')

def handle_cloudgetnode(bot, ievent):
    """ cloud-getnode .. show node of <name>  """
    if not cfg.get('enable'):
        ievent.reply('cloud is not enabled')
        return
    try:
        name = ievent.args[0]
    except IndexError:
        ievent.missing('<name>')
        return
    node = cloud.byname(name)
    if not node:
        ievent.reply('there is no node named %s' % name)
        return
    ievent.reply(str(node))
 
cmnds.add('cloud-getnode', handle_cloudgetnode, 'OPER')
examples.add('cloud-getnode', 'cloud-getnode <name> .. get node of <name>', \
'cloud-getnode gozerbot.org')

def handle_cloudnames(bot, ievent):
    """ cloud-names .. show names with nodes in cache """
    if not cfg.get('enable'):
        ievent.reply('cloud is not enabled')
        return
    ievent.reply("cloud node names: ", cloud.names(), dot=True)
 
cmnds.add('cloud-names', handle_cloudnames, 'OPER')
examples.add('cloud-names', 'show all node names', 'cloud-names')

def handle_cloudboot(bot, ievent):
    """ boot the cloud node cache """
    if not cfg.get('enable'):
        ievent.reply('cloud is not enabled')
        return
    try:
        url = ievent.args[0]
    except IndexError:
        url = 'http://gozerbot.org:10101'
    start = time.time()
    teller = 0
    def cb(client, result):
        if result.error:
            ievent.reply('boot error: %s' % result.error)
            return 
        for node in cloud.nodes.values():
            if node.synced > start:
                teller += 1
        ievent.reply('booted %s nodes' % str(teller))
    cloud.boot(cfg.get('name'), cfg.get('port'), url, cbin=cb)
    ievent.closequeue=False
 
cmnds.add('cloud-boot', handle_cloudboot, 'OPER', threaded=True)
examples.add('cloud-boot', 'sync cloud nodes list with provided host', \
'1) cloud-boot 2) cloud-boot http://gozerbot.org:10101')

def handle_cloudfullboot(bot, ievent):
    """ cloud-fullboot .. boot from all nodes in cache """
    if not cfg.get('enable'):
        ievent.reply('cloud is not enabled')
        return
    start = time.time()
    teller = 0
    def cb(client, result):
        if result.error:
            ievent.reply('boot error: %s' % result.error)
            return 
        for node in cloud.nodes.values():
            if node.synced > start:
                teller += 1
        ievent.reply('booted %s nodes' % str(teller))
    cloud.fullboot(cbin=cb)
    ievent.closequeue = False
 
cmnds.add('cloud-fullboot', handle_cloudfullboot, 'OPER')
examples.add('cloud-fullboot', 'do a boot on every node in the cloud node \
list', 'cloud-boot')

def handle_cloudremove(bot, ievent):
    if not cfg.get('enable'):
        ievent.reply('cloud is not enabled')
        return
    if not ievent.rest:
        ievent.missing('<name>')
        return
    got = False
    try:
        url = cloud.state['names'][ievent.rest]
        if url:
            cloud.unpersist(url)
            cloud.remove(url)
            got = True
    except KeyError:
        ievent.reply('there is no %s cloud node' % ievent.rest)
        return
    except Exception, ex:
        ievent.reply('error removing %s: %s' % (ievent.rest, str(ex)))
        return
    if got:
        ievent.reply('%s node removed' % ievent.rest)
    else:
        ievent.reply('error removing %s node' % ievent.rest)

cmnds.add('cloud-remove', handle_cloudremove, 'OPER')
examples.add('cloud-remove', 'remove node with <name> from the cloud' , \
'cloud-remove gozerbot.org')

def handle_cloudjoin(bot, ievent):
    if not cfg.get('enable'):
        ievent.reply('cloud is not enabled')
        return
    if not ievent.rest:
        ievent.missing('<name>')
        return
    def cb(client, result):
        if result.error:
            ievent.reply(result.error)
        else:
            ievent.reply(result.data)
    try:
        url = cloud.state['names'][ievent.rest]
        cloud.join(cfg.get('name'), cfg.get('port'), url, cb)
    except Exception, ex:
        ievent.reply('error joining %s: %s' % (ievent.rest, str(ex)))
        return
    ievent.reply('join reqeust sent to %s' % url)
    ievent.closequeue = False

cmnds.add('cloud-join', handle_cloudjoin, 'OPER', allowqueue=False)
examples.add('cloud-join', 'join node with <name>' , 'cloud-join gozerbot.org')

def handle_cloudjoinall(bot, ievent):
    if not cfg.get('enable'):
        ievent.reply('cloud is not enabled')
        return
    def cb(client, result):
        if result.error:
            ievent.reply("%s: %s" %(client.name, result.error))
        else:
            ievent.reply("%s: %s" % (client.name, result.data))
    try:
        cloud.joinall(cfg.get('name'), cfg.get('port'), cb)
    except Exception, ex:
        handle_exception()
        ievent.reply('error joining %s: %s' % (ievent.rest, str(ex)))
        return
    ievent.reply('join requests sent')
    ievent.closequeue = False

cmnds.add('cloud-joinall', handle_cloudjoinall, 'OPER', allowqueue=False)
examples.add('cloud-joinall', 'join all nodes' , 'cloud-joinall')

def handle_cloudmeet(bot, ievent):
    if not ievent.rest:
        ievent.missing('<nodename>')
        return
    name = ievent.rest
    node = cloud.byname(name)
    if not node:
       ievent.reply('%s is not a cloud node' % name)
       return
    if not node.client.host:
       ievent.reply("can't determine host of %s" % name)
       return
    try:
        if not users.exist(name):
            users.add(name, ["cloud@%s" % node.client.host, ], ['CLOUD', ])
            ievent.reply("%s (%s) added to database" % (name, node.client.host))
        else:
            ievent.reply("%s node already exists" % name)
    except Exception, ex:
        ievent.reply('error adding %s to the database: %s' % (name, str(ex)))

cmnds.add('cloud-meet', handle_cloudmeet, 'OPER')
examples.add('cloud-meet', 'cloud-meet <nodename>', 'cloud-meet gozerbot.org')

def handle_cloudallow(bot, ievent):
    """ cloud-allow .. allow a server mountpoint """
    if not cfg.get('enable'):
        ievent.reply('cloud is not enabled')
        return
    if not ievent.rest:
        ievent.missing('<server mount>')
        return
    if server:
        server.enable(('gozernet', ievent.rest))
        ievent.reply('%s allowed' % ievent.rest)
    else:
        ievent.reply('cloud server not enabled')

cmnds.add('cloud-allow', handle_cloudallow, 'OPER')
examples.add('cloud-allow', 'allow execution of a server mountpoint', \
'cloud-allow auth')

def handle_clouddisallow(bot, ievent):
    """ cloud-disallow .. disallow a mount point"""
    if not cfg.get('enable'):
        ievent.reply('cloud is not enabled')
        return
    if not ievent.rest:
        ievent.missing('<server mount>')
        return
    if server:
        server.disable(('gozernet', ievent.rest))
        ievent.reply('%s disallowed' % ievent.rest)
    else: 
        ievent.reply('cloud server not enabled')

cmnds.add('cloud-disallow', handle_clouddisallow, 'OPER')
examples.add('cloud-disallow', 'disallow execution of a server mountpoint', \
'cloud-disallow auth')

def handle_cloudstartserver(bot, ievent):
    """ cloud-startserver .. start the cloud server """
    if not cfg.get('enable'):
        ievent.reply('cloud is not enabled')
        return
    cfg.set('servermode', 1)
    cfg.save()
    start_new_thread(startserver, ())
    ievent.reply('server thread started')
 
cmnds.add('cloud-startserver', handle_cloudstartserver, 'OPER')
examples.add('cloud-startserver', 'start the cloudserver', 'cloud-startserver')

def handle_cloudstopserver(bot, ievent):
    """ cloud-disallow .. disallow a mount point"""
    cfg.set('servermode', 0)
    cfg.save()
    stopserver()
    ievent.reply('server disabled')
 
cmnds.add('cloud-stopserver', handle_cloudstopserver, 'OPER')
examples.add('cloud-stopserver', 'stop the cloud server', \
'cloud-stopserver')

