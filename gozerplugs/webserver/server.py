# plugs/webserver.py
#
#

""" allow commands to be called through a web server """

__copyright__ = 'this file is in the public domain'
__credits__ = 'thanks to John Munn (jrmunn@home.com) for his form focus \
javascript'
__gendocfirst__ = ['web-enable', ]
__gendoclast__ = ['web-disable', ]

from gozerbot.threads.thr import start_new_thread
from gozerbot.generic import rlog, handle_exception
from gozerbot.commands import cmnds
from gozerbot.plugins import plugins
from gozerbot.gozerimport import gozer_import
from gozerbot.users import users
from gozerbot.plughelp import plughelp
from gozerbot.examples import examples
from gozerbot.config import config
from gozerbot.aliases import aliasset
from gozerbot.persist.persistconfig import PersistConfig
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
from urllib import unquote_plus
from cgi import escape
import time, sys, select, types

plughelp.add('webserver', 'maintain the bots webserver')

cfg = PersistConfig()
cfg.define('webenable', 0)
cfg.define('webport', 8088)
cfg.define('webhost', '')
cfg.define('whitelist', [])
cfg.define('whitelistenable', 1)
cfg.define('blacklist', [])
cfg.define('showplugs', ['infoitems', 'karma', 'quotes'])
cfg.define('denyplugs', [])
cfg.define('deleteenable', 0)

#cfg.syncold(datadir + os.sep + 'web')
doit =  cfg.get('webenable')
if not doit:
    rlog(10, 'webserver', 'not enabled')
else:
    if not users.getname('web@web'):
        users.add('web', ['web@web', ], ['WEB', ])
webhostname = cfg.get('webhost')
webport = cfg.get('webport')

def init():
    """ init webserver plugin """
    global httpd
    try:
        if doit:
            httpd = BotHTTPServer((webhostname, webport), BotHTTPRequestHandler)
    except Exception, ex:
        rlog(10, 'webserver', "can't start server: %s" % str(ex))
        return 0
    if httpd:
        webplugs = gozer_import('gozerplugs.webserver.webplugs')
        for i in webplugs.__all__:
            if i not in cfg.get('denyplugs'):
                try:
                    httpd.reloadhandler(i)
                except:
                    handle_exception()
        start_new_thread(httpd.run, ())
    return 1
    
def shutdown():
    """ shutdown webserver plugin """
    global httpd
    if not httpd:
        return 1
    try:
        httpd.stop = True
        httpd.server_close()
    except:
        handle_exception()
        pass
    time.sleep(3)
    return 1

class BotHTTPServer(ThreadingMixIn, HTTPServer):

    """ bots web server """

    allow_reuse_address = True
    daemon_thread = True

    def __init__(self, addr, handler):
        self.stop = False
        self.addr = addr
        self.dontshow = ['nodes', 'ping', 'dispatch', 'join']
        self.handlers = {}
        self.webmods = {}
        HTTPServer.__init__(self, addr, handler)
        self.poll = select.poll()
        self.poll.register(self.socket)

    def addhandler(self, txt, handler):
        """ add a web handler """
        self.handlers[txt] = handler
        rlog(0, 'webserver', '%s handler added' % txt)

    def reloadhandler(self, mod):
        """ reload web handler """
        try:
            module = sys.modules['gozerplugs.webserver.webplugs.%s' % mod]
            reload(module)
            self.webmods[mod] = module
        except KeyError:
            self.webmods[mod] = gozer_import('gozerplugs.webserver.webplugs.%s' % mod)

    def do(self, request):
        """ do a request """
        path = request.path.split('?')[0]
        splitted = path.split('/')
        if len(splitted) > 2:
            ppath = '/'.join(splitted[:-1])
        else:
            ppath = path
        request.value = splitted[-1]
        if self.handlers.has_key(ppath):
            func = self.handlers[ppath]
            try:
                result = func(request)
            except Exception, ex:
                handle_exception()
                result = None
            return result
        else:
            return None

    def handle_error(self, request, addr):
        """ log the error """
        rlog(10, 'webserver', 'error: %s %s' % (sys.exc_type, sys.exc_value))

    def run(self):
        """ webservers main loop """
        rlog(10, 'webserver', 'starting')
        while not self.stop:
            try:
                todo = self.poll.poll(1000)
            except:
                continue
            if todo:
                self.handle_request()
                time.sleep(0.001)
        rlog(10, 'webserver', 'stopping')

focustxt = """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
   "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title>GOZERBOT</title>
<script type="text/javascript">

<!-- This script and many more are available free online at -->
<!-- The JavaScript Source!! http://javascript.internet.com -->
<!-- John Munn  (jrmunn@home.com) -->

<!-- Begin
 function putFocus(formInst, elementInst) {
  if (document.forms.length > 0) {
   document.forms[formInst].elements[elementInst].focus();
  }
 }
// The second number in the "onLoad" command in the body
// tag determines the form's focus. Counting starts with '0'
//  End -->
</script>

</head>
<body onLoad="putFocus(0,0);">
""" 

endtxt = """</body>
</html>
"""

def writeheaderplain(request):
    request.send_response(200)
    request.send_header('Content-type', 'text/plain; charset=%s' % \
sys.getdefaultencoding())
    request.send_header('Server', config['version'])
    request.end_headers()

def writeheaderhtml(request):
    request.send_response(200)
    request.send_header('Content-type', 'text/html; charset=%s' % \
sys.getdefaultencoding())
    request.send_header('Server', config['version'])
    request.end_headers()

def webheader(request):
    """ create web header """
    request.wfile.write('<form action="dispatch">')
    request.wfile.write('Command <input name="command"></form><br>')
    cmndslist = cmnds.list('WEB')
    cmndslist.sort()
    request.wfile.write('the bot allows the following commands: .. \
<p>%s</p>' \
% ' '.join(cmndslist))
    request.wfile.write('use chan #channel to provide a channel for \
channel related commands<br>example: search http chan #dunkbots<br><br>')
    #for i in cfg.get('showplugs'):
    #    request.wfile.write("<a href='/%s'>%s</a>" % (i, i))
    #    request.wfile.write("    ")
    request.wfile.write('<br>')

def sendresult(request, result, how=[]):
    if not result:
        return
    if type(result) == types.StringType:
        result = [result, ]
    for i in result:
        output = i
        if 'escape' in how:
            output = escape(output)
        request.wfile.write(output)
        if 'break' in how:
            request.wfile.write("<br>")
        if 'newline' in how:
            request.wfile.write("\n")
    return True

def makeresult(request):
    try:
        result = request.server.do(request)
    except:
        handle_exception()
        return
    if result:
        return result

class BotHTTPRequestHandler(BaseHTTPRequestHandler):

    """ bots request handler class """

    def entrypoint(self):
        ip = self.client_address[0]
        if not cfg.get('whitelistenable') and ip in cfg.get('blacklist'):
            rlog(100, 'webserver', 'denied %s' % ip)
            self.send_error(404)
            return False
        if  cfg.get('whitelistenable') and ip not in cfg.get('whitelist'):
            rlog(100, 'webserver', 'denied %s' % ip)
            self.send_error(404)
            return False
        return True

    def do_DELETE(self):
         if not self.entrypoint():
            return
         writeheaderplain(self)
         sendresult(self, makeresult(self))

    def do_POST(self):
        """ called on POST """
        if not self.entrypoint():
            return
        writeheaderplain(self)
        sendresult(self, makeresult(self))

    def do_GET(self): 
        """ called on GET """
        if not self.entrypoint():
            return
        if self.path == '/' or self.path.startswith('/dispatch'):
            writeheaderhtml(self)
            self.wfile.write(focustxt)
            self.wfile.write("<h1>GOZERBOT</h1>")
            webheader(self)
            self.wfile.write(endtxt)
            result = makeresult(self)
            if result:
                self.wfile.write('<h2>results</h2>')
                sendresult(self, result, ['break', 'escape', 'newline'])
        elif self.path.startswith('/json'):
            result = makeresult(self)
            self.wfile.write(result)
        else:
            result = makeresult(self)
            if result:
                writeheaderplain(self)
                sendresult(self, result, ['newline', ])
            else:
                writeheaderplain(self)
                sendresult(self, 'no data')
        self.wfile.close()

    #localhost - - [18/Mar/2006 14:51:53] "GET / HTTP/1.1" 200 -
    def log_request(self, code, size='-'):
        """ log the request """
        if 'ping' in self.path:
            rlog(1, 'webserver', '%s "%s %s" %s %s %s' % \
(self.address_string(), self.command, self.path, self.request_version, code ,\
size))
        else:
            rlog(10, 'webserver', '%s "%s %s" %s %s %s' % \
(self.address_string(), self.command, self.path, self.request_version, code ,\
size))

    def log_error(self, mask, *txt):
        """ log the error """
        rlog(10, 'webserver', self.address_string() + ' ' + mask % txt)

httpd = None
    
def handle_web(bot, ievent):
    """ web .. show on which host:port webserver is running """
    if httpd:
        ievent.reply("web server is running at http://%s:%s" % \
httpd.addr)
    else:
        ievent.reply("webserver is not running")
        
cmnds.add('web', handle_web, 'USER')
examples.add('web', 'show what web adress we are running on', 'web')

def handle_webenable(bot, ievent):
    """ web-enable <host> <port> """
    try:
        (host, port) = ievent.args
        port = int(port)
    except ValueError:
        ievent.missing('<host> <port>')
        return
    cfg.set('webenable', 1)
    cfg.set('webhost', host)
    cfg.set('webport', port)
    cfg.save()
    if plugins.reload('gozerplugs', 'webserver'):
        ievent.reply('done')
    else:
        ievent.reply('error reloading webserver plugin')
        
cmnds.add('web-enable', handle_webenable, 'OPER', threaded=True)
examples.add('web-enable', 'web-enable <host> <port> .. enable the \
webserver', 'web-enable localhost 8088')

def handle_webdisable(bot, ievent):
    """ web-disable .. disable webserver"""
    cfg.set('webenable', 0)
    cfg.save()
    if plugins.reload('gozerplugs', 'webserver'):
        ievent.reply('done')
    else:
        ievent.reply('error reloading webserver plugin')

cmnds.add('web-disable', handle_webdisable, 'OPER')
examples.add('web-disable', 'disable the webserver', 'web-disable')

def handle_webreload(bot, ievent):
    """ web-reload <handler> """
    if not httpd:
        ievent.reply('webserver is not running')
        return
    try:
        what = ievent.args[0]
    except IndexError:
        ievent.missing('<handler>')
        return
    try:
        httpd.reloadhandler(what)
    except Exception, ex:
        handle_exception(ievent)
        return
    ievent.reply('%s reloaded' % what)

cmnds.add('web-reload', handle_webreload, 'OPER')
examples.add('web-reload', 'web-reload <handler> .. reload a web handler', \
'web-reload dispatch')

def handle_weballowip(bot, ievent):
    """ web-allowip <ipnr> """
    if not httpd:
        ievent.reply('webserver is not running')
        return
    try:
        what = ievent.args[0]
    except:
        ievent.missing('<ipnr>')
    cfg.append('whitelist', what)
    try:
        cfg.remove('blacklist', what)
    except ValueError:
        pass
    cfg.save()
    ievent.reply('%s allowed' % what)

cmnds.add('web-allowip', handle_weballowip, 'OPER')
examples.add('web-allowip', 'web-allowip <ipnr> .. add ip to whitelist and \
remove from blacklist', 'web-allowip 127.0.0.1')

def handle_webdenyip(bot, ievent):
    """ web-denyip <ipnr> """
    if not httpd:
        ievent.reply('webserver is not running')
        return
    try:
        what = ievent.args[0]
    except IndexError:
        ievent.missing('<ipnr>')
        return
    if what not in cfg.get('blacklist'):
        cfg.append('blacklist', what)
    try:
        cfg.remove('whitelist', what)
    except ValueError:
        pass
    cfg.save()
    ievent.reply("%s denied" % what)

cmnds.add('web-denyip', handle_webdenyip, 'OPER')
examples.add('web-denyip', 'web-denyip <ipnr> .. remove from whitelist and \
add to blacklist', 'web-denyip 127.0.0.1')

def handle_weblists(bot, ievent):
    """ web-lists .. show black and white lists"""
    ievent.reply("whitelist: %s blacklist: %s" % (cfg.get('whitelist'), \
cfg.get('blacklist')))

cmnds.add('web-lists', handle_weblists, 'OPER')
examples.add('web-lists', 'show webservers white and black lists', \
'web-lists')

def handle_webdefaultallow(bot, ievent):
    """ web-defaultallow .. put webserver in default allow mode """
    cfg.set('whitelistenable', 0)
    ievent.reply('ok')

cmnds.add('web-defaultallow', handle_webdefaultallow, 'OPER')
examples.add('web-defaultallow', 'set webservers mode to defaultallow .. \
all ips except those in the blacklist', 'web-defaultallow')

def handle_webdefaultdeny(bot, ievent):
    """ web-defaultdeny .. put webserver in default deny mode """
    cfg.set('whitelistenable', 1)
    ievent.reply('ok')

cmnds.add('web-defaultdeny', handle_webdefaultdeny, 'OPER')
examples.add('web-defaultdeny', 'put webserver in default deny mode .. only \
allow ips in whitelist', 'web-defaultdeny')

def handle_disablehandler(bot, ievent):
    """ disable a web handler """
    if not httpd:
        ievent.reply('webserver is not running')
        return
    try:
        handler = ievent.args[0]
    except IndexError:
        ievent.missing('<handler>')
        return
    try:
        del httpd.handlers[handler]
        if handler in cfg.get('showplugs'):
            cfg.remove('showplugs', handler)
        if handler not in cfg.get('denyplugs'):
            cfg.append('denyplugs', handler)
        ievent.reply('%s handler disabled' % handler)
    except KeyError:
        ievent.reply('%s handler is not enabled' % handler)

cmnds.add('web-disablehandler', handle_disablehandler, 'OPER')
examples.add('web-disablehandler', 'disable web plugin', 'web-disablehandler \
quotes')

def handle_enablehandler(bot, ievent):
    """ enable a web handler """
    if not httpd:
        ievent.reply('webserver is not running')
        return
    try:
        handler = ievent.args[0]
    except IndexError:
        ievent.missing('<handler>')
        return
    try:
        if handler in cfg.get('denyplugs'):
            cfg.remove('denyplugs', handler)
        httpd.reloadhandler(handler)
        ievent.reply('%s handler enabled' % handler)
    except:
        ievent.reply('failed to enable %s handler' % handler)

cmnds.add('web-enablehandler', handle_enablehandler, 'OPER')
examples.add('web-enablehandler', 'enable web plugin', 'web-enablehandler \
quotes')

aliasset('web-cfg', 'server-cfg')
