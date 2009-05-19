# gozerbot/rest/client.py
#
#

""" Rest Client class """

from gozerbot.generic import geturl3, geturl4, posturl, deleteurl, rlog, \
handle_exception, useragent, lockdec, exceptionmsg
from simplejson import loads
from urllib2 import HTTPError, URLError
from httplib import InvalidURL
from urlparse import urlparse
import socket, asynchat, urllib, sys, thread, re, asyncore

restlock = thread.allocate_lock()
locked = lockdec(restlock)

class RestResult(object):

    def __init__(self, url="", name=""):
        self.url = url
        self.name = name
        self.data = None
        self.error = None
        self.status = None
        self.reason = ""

class RestClient(object):

    def __init__(self, url, keyfile=None, certfile=None, port=None):
        if not url.endswith('/'):
            url += '/'
        try:
            u = urlparse(url)
            splitted = u[1].split(':')
            if len(splitted) == 2:
                host, port = splitted
            else:
                host = splitted[0]
                port = port or 9999
            path = u[2]
        except Exception, ex:
            raise
        self.host = host 
        self.path = path
        self.port = port
        self.url = url
        self.keyfile = keyfile
        self.certfile = certfile
        self.callbacks = []

    def addcb(self, callback): 
        if not callback: 
            return
        self.callbacks.append(callback)
        rlog(0, self.name, 'added callback %s' % str(callback))
        return self

    def delcb(self, callback):
        try:
            del self.callbacks[callback]
            rlog(0, self.name, 'deleted callback %s' % str(callback))
        except ValueError:
            pass
        
    def do(self, func, url, *args, **kwargs):
        result = RestResult(url)
        try:
            res = func(url, {}, kwargs, self.keyfile, self.certfile, self.port)
            result.status = res.status
            result.reason = res.reason
            if result.status >= 400:
                result.error = result.status
            else:
                result.error = None
            if result.status == 200:
                result.data = loads(res.read())
            else:
                result.data = None
        except Exception, ex:
            result.error = str(ex)
            result.data = None
        for cb in self.callbacks:
            try:
                cb(self, result)
                rlog(0, self.name, 'called callback %s' % str(cb))
            except Exception, ex:
                handle_exception()
        return result

    def post(self, *args, **kwargs):
        return self.do(posturl, self.url, *args, **kwargs)

    def add(self, *args, **kwargs):
        return self.do(posturl, self.url, *args, **kwargs)

    def delete(self, nr=None):
         if nr:
             return self.do(deleteurl, self.url + '/' + str(nr))
         else:
             return self.do(deleteurl, self.url)

    def get(self, nr=None):
        if not nr:
            return self.do(geturl4, self.url)
        else:
            return self.do(geturl4, self.url + '/' + str(nr))

class RestClientAsync(RestClient, asynchat.async_chat):

    def __init__(self, url, name=""):
        RestClient.__init__(self, url)
        asynchat.async_chat.__init__(self)
        self.set_terminator("\r\n\r\n")
        self.reading_headers = True
        self.error = None
        self.buffer = ''
        self.name = name or self.url
        self.headers = {}
        self.status = None

    def handle_error(self):
        exctype, excvalue, tb = sys.exc_info()
        if exctype == socket.error:
            try:
                errno, errtxt = excvalue
                if errno in [11, 35, 9]:
                    return
            except ValueError:
                pass
            self.error = str(excvalue)
        else:
            rlog(10, self.name, exceptionmsg())
            self.error = exceptionmsg()
        self.buffer = ''
        self.close()
        result = RestResult(self.url, self.name)
        result.error = self.error
        result.data = None
        for cb in self.callbacks:
            try:
                cb(self, result)
                rlog(0, self.name, 'called callback %s' % str(cb))
            except Exception, ex:
                handle_exception()

    def handle_expt(self):
        pass

    def handle_connect(self):
        rlog(0, self.name, 'connected')

    def start(self):
        assert(self.host)
        assert(int(self.port))
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.connect((self.host, int(self.port)))
            #self.connect((self.host, int(self.port)))
            rlog(0, self.name, 'started client')
        except socket.error, ex:
            self.error = str(ex)
        except Exception, ex:
            rlog(10, self.name, "can't start %s" % str(ex))

    def found_terminator(self):
        if self.reading_headers:
            try:
                self.headers = self.buffer.split('\r\n')
                self.status = int(self.headers[0].split()[1])
            except (ValueError, IndexError):
                handle_exception()
            self.buffer = ''
            self.reading_headers = False
            rlog(5, self.name, 'headers: %s' % self.headers)

    def collect_incoming_data(self, data):
        self.buffer = self.buffer + data

    def handle_close(self):
        self.handle_incoming()
        self.close()

    def handle_incoming(self):
        rlog(5, self.name, "incoming: " + self.buffer)
        if not self.reading_headers:
            result = RestResult(self.url, self.name)
            if self.status >= 400:
                rlog(10, self.name, 'error status: %s' % self.status)  
                result.error = self.status
                result.data = None
            elif self.error:
                result.error = self.error
                result.data = None
            elif self.buffer == "None":
                result.data = ""
                result.error = None
            else:
                try:
                    res = loads(self.buffer)
                    if not res:
                        self.buffer = ''
                        return
                    result.data = res
                    result.error = None
                except ValueError, ex:
                    rlog(10, self.name, "can't decode %s" % self.buffer)
                    result.error = str(ex)
                except Exception, ex:
                    rlog(10, self.name, exceptionmsg())
                    result.error = exceptionmsg()                
                    result.data = None
            for cb in self.callbacks:
                try:
                    cb(self, result)
                    rlog(0, self.name, 'called callback %s' % str(cb))
                except Exception, ex:
                    handle_exception()
            self.buffer = ''

    def dorequest(self, method, path, postdata={}, headers={}):
        if postdata:
            postdata = urllib.urlencode(postdata)
        if headers:
            if not headers.has_key('Content-Length'):
                headers['Content-Length'] = len(postdata)
            headerstxt = ""
            for i,j in headers.iteritems():
                headerstxt += "%s: %s\r\n" % (i.lower(), j)
        else:
            headerstxt = ""
        if method == 'POST':
            s = "%s %s HTTP/1.0\r\n%s\r\n%s\r\n\r\n" % (method, path, \
headerstxt, postdata)
        else:
            s = "%s %s HTTP/1.0\r\n\r\n" % (method, path)
        self.start()
        rlog(0, self.url, 'sending %s' % s)
        self.push(s)

    def sendpost(self, postdata):
        headers = {'Content-Type': 'application/x-www-form-urlencoded', \
'Accept': 'text/plain; text/html', 'User-Agent': useragent()}
        self.dorequest('POST', self.path, postdata, headers)

    def sendget(self):
        headers = {'Content-Type': 'text/html', \
'Accept': 'text/plain; text/html', 'User-Agent': useragent()}
        self.dorequest('GET', self.path)

    def post(self, *args, **kwargs):
        self.sendpost(kwargs)

    def get(self):
        self.sendget()
