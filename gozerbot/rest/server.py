# gozerbot/rest/server.py
#
#

__copyright__ = 'this file is in the public domain'

from gozerbot.generic import rlog, handle_exception, calledfrom, exceptionmsg
from gozerbot.config import config
from gozerbot.persist.persiststate import ObjectState
from gozerbot.threads.thr import start_new_thread
from SocketServer import BaseServer, ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from urllib import unquote_plus
from asyncore import dispatcher
from cgi import escape
import time, sys, select, types, socket

class RestServerBase(HTTPServer):

    """ REST web server """

    allow_reuse_address = True
    daemon_thread = True

    def start(self):
        self.name = calledfrom(sys._getframe(0))
        self.stop = False
        self.running = False
        self.handlers = {}
        self.webmods = {}
        self.state = ObjectState()
        self.state.define('whitelistenable', 0)
        self.state.define('whitelist', [])
        self.state.define('blacklist', [])
        self.state.define('disable', [])
        self.poll = select.poll()
        self.poll.register(self)
        start_new_thread(self.serve, ())
        time.sleep(1)

    def shutdown(self):
        try:
            self.stop = True
            self.socket.shutdown(2)
            self.socket.close()
            time.sleep(2)
            self.server_close()
        except Exception, ex:
            handle_exception()

    def serve(self):
        rlog(10, self.name, 'starting server')
        while not self.stop:
            self.running = True
            try:
                got = self.poll.poll(100)
            except Exception, ex:
                handle_exception()
            if got:
                self.handle_request()
            #time.sleep(0.001)
        self.running = False
        rlog(10, self.name, 'stopping server')

    def entrypoint(self, request):
        ip = request.ip
        if not self.whitelistenable() and ip in self.blacklist():
            rlog(100, self.name, 'denied %s' % ip)
            request.send_error(401)
            return False
        if  self.whitelistenable() and ip not in self.whitelist():
            rlog(100, self.name, 'denied %s' % ip)
            request.send_error(401)
            return False
        return True

    def whitelistenable(self): 
        return self.state['whitelistenable']

    def whitelist(self): 
        return self.state['whitelist']

    def blacklist(self): 
        return self.state['blacklist']

    def addhandler(self, path, type, handler):
        """ add a web handler """
        splitted = []
        for i in path.split('/'):
            if i:
                splitted.append(i)
        splitted = tuple(splitted)
        if not self.handlers.has_key(splitted):
            self.handlers[splitted] = {}
        self.handlers[splitted][type] = handler
        rlog(0, self.name, '%s %s handler added' % (splitted, type))

    def enable(self, what):
        try:
            self.state['disable'].remove(what)
            rlog(10, self.name, 'enabled %s' % str(what))
        except ValueError:
            pass

    def disable(self, what):
        self.state['disable'].append(what)
        rlog(10, self.name, 'enabled %s' % str(what))

    def do(self, request):
        """ do a request """
        path = request.path.split('?')[0]
        if path.endswith('/'):
            path = path[:-1]
        splitted = []
        for i in path.split('/'):
            if i:
                splitted.append(i)
        splitted = tuple(splitted)
        for i in self.state['disable']:
            if i in splitted:
                rlog(10, self.name, 'denied disabled %s' % i)
                request.send_error(404)
                return
        request.splitted = splitted
        request.value = None
        type = request.command
        try:
            func = self.handlers[splitted][type]
        except (KeyError, ValueError):
            try:
                func = self.handlers[splitted[:-1]][type]
                request.value = splitted[-1]
            except (KeyError, ValueError):
                request.send_error(404)
                return
        result = func(self, request)
        return result

    def handle_error(self, request, addr):
        """ log the error """
        exctype, excvalue, tb = sys.exc_info()
        if exctype == socket.timeout:
            rlog(10, self.name, 'socket timeout on %s' % str(addr))
            return
        if exctype == socket.error:
            rlog(10, self.name, 'socket error on %s: %s' % (str(addr), excvalue))
            return
        exceptstr = exceptionmsg()
        rlog(10, self.name, 'error on %s: %s %s => %s' % (str(addr), exctype, \
excvalue, exceptstr))


class RestServer(ThreadingMixIn, RestServerBase):

    pass

class RestServerAsync(RestServerBase, dispatcher):

    pass

class RestRequestHandler(BaseHTTPRequestHandler):

    """ timeserver request handler class """

    def setup(self):
        BaseHTTPRequestHandler.setup(self)
        self.ip = self.client_address[0]
        self.name = self.ip
        if not hasattr(self, 'path'):
            self.path = "not set"
        self.size = 0

    def writeheader(self, type='text/plain'):
        self.send_response(200)
        self.send_header('Content-type', '%s; charset=%s ' % (type,\
sys.getdefaultencoding()))
        self.send_header('Server', config['version'])
        self.end_headers()

    def sendresult(self):
        try:
            result = self.server.do(self)
            if not result:
                return
            self.size = len(result)
        except Exception, ex:
            handle_exception()
            self.send_error(501)
            return
        self.writeheader()
        self.wfile.write(result)
        self.wfile.close()

    def handle_request(self):
        if not self.server.entrypoint(self):
            return
        self.sendresult()

    do_DELETE = do_PUT = do_GET = do_POST = handle_request

    def log_request(self, code):
        """ log the request """
        try:
            ua = self.headers['user-agent']
        except:
            ua = "-"
        try:
            rf = self.headers['referer']
        except:
            rf = "-"

        rlog(10, self.name, '%s "%s %s %s" %s %s "%s" "%s"' % \
(self.address_string(), self.command, self.path, self.request_version, code, \
self.size, rf, ua))

try:
    from OpenSSL import SSL

    class SecureRestServer(RestServer):

        def __init__(self, server_address, HandlerClass, keyfile, certfile):
            BaseServer.__init__(self, server_address, HandlerClass)
            ctx = SSL.Context(SSL.SSLv23_METHOD)
            ctx.set_options(SSL.OP_NO_SSLv2)
            rlog(10, self.name, "loading private key from %s" % keyfile)
            ctx.use_privatekey_file (keyfile)
            rlog(10, self.name, 'loading certificate from %s' % certfile)
            ctx.use_certificate_file(certfile)
            rlog(10, self.name, 'creating SSL socket on %s' % \
str(server_address))
            self.socket = SSL.Connection(ctx, socket.socket(self.address_family,
                                                        self.socket_type))
            self.server_bind()  
            self.server_activate()

    class SecureAuthRestServer(SecureRestServer):

        def __init__(self, server_address, HandlerClass, chain, serverkey, \
servercert):
            BaseServer.__init__(self, server_address, HandlerClass)
            ctx = SSL.Context(SSL.SSLv23_METHOD)
            rlog(10, self.name, "loading private key from %s" % serverkey)
            ctx.use_privatekey_file (serverkey)
            rlog(10, self.name, 'loading certificate from %s' % servercert)
            ctx.use_certificate_file(servercert)
            rlog(10, self.name, 'loading chain of certifications from %s' % \
chain)
            ctx.set_verify_depth(2)
            ctx.load_client_ca(chain)
            #ctx.load_verify_locations(chain)
            rlog(10, self.name, 'creating SSL socket on %s' % \
str(server_address))
            callback = lambda conn,cert,errno,depth,retcode: retcode
            ctx.set_verify(SSL.VERIFY_FAIL_IF_NO_PEER_CERT | SSL.VERIFY_PEER, \
callback)
            ctx.set_session_id('gozerbot')
            self.socket = SSL.Connection(ctx, socket.socket(self.address_family,
                                                        self.socket_type))
            self.server_bind()  
            self.server_activate()

    class SecureRequestHandler(RestRequestHandler):

        def setup(self):
            self.connection = self.request._sock
            self.request._sock.setblocking(1)
            self.rfile = socket._fileobject(self.request, "rb", self.rbufsize)
            self.wfile = socket._fileobject(self.request, "wb", self.rbufsize)

except ImportError:
    rlog(10, 'rest.server', 'no SSL detected .. see python-openssl')
  