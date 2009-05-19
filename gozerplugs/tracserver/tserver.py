# gozerplugs/tracserver/tracserver.py
# -*- coding: utf-8 -*-
#
# taken from the standalone app
#
# Copyright (C) 2003-2009 Edgewall Software
# Copyright (C) 2003-2005 Jonas Borgström <jonas@edgewall.com>
# Copyright (C) 2005-2006 Matthew Good <trac@matt-good.net>
# Copyright (C) 2005-2006 Christopher Lenz <cmlenz@gmx.de>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://trac.edgewall.org/wiki/TracLicense.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://trac.edgewall.org/log/.
#
# Author: Jonas Borgström <jonas@edgewall.com>
#         Matthew Good <trac@matt-good.net>
#         Christopher Lenz <cmlenz@gmx.de>

""" trac server plugin. """

from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.threads.thr import start_new_thread
from gozerbot.plughelp import plughelp
from gozerbot.plugins import plugins
from gozerbot.utils.log import rlog
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.datadir import datadir

try:
    from trac import __version__ as VERSION
    from trac.util import autoreload, daemon
    from trac.web.auth import BasicAuthentication, DigestAuthentication
    from trac.web.main import dispatch_request
    from trac.web.wsgi import WSGIServer, WSGIRequestHandler
    gottrac = True
except ImportError:
    gottrac = False        

from SocketServer import ThreadingMixIn

import os, sys, time, socket, select

cfg = PersistConfig()
cfg.define('startup', '%s --port 10102 -s' % (datadir + os.sep + 'trac'))

plughelp.add('tserver', 'trac server')

if not os.path.isdir(datadir + os.sep + 'trac'):
    os.mkdir(datadir + os.sep + 'trac')

class AuthenticationMiddleware(object):

    def __init__(self, application, auths, single_env_name=None):
        self.application = application
        self.auths = auths
        self.single_env_name = single_env_name
        if single_env_name:
            self.part = 0
        else:
            self.part = 1

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        path_parts = filter(None, path_info.split('/'))
        if len(path_parts) > self.part and path_parts[self.part] == 'login':
            env_name = self.single_env_name or path_parts[0]
            if env_name:
                auth = self.auths.get(env_name, self.auths.get('*'))
                if auth:
                    remote_user = auth.do_auth(environ, start_response)
                    if not remote_user:
                        return []
                    environ['REMOTE_USER'] = remote_user
        return self.application(environ, start_response)


class BasePathMiddleware(object):

    def __init__(self, application, base_path):
        self.base_path = '/' + base_path.strip('/')
        self.application = application

    def __call__(self, environ, start_response):
        path = environ['SCRIPT_NAME'] + environ.get('PATH_INFO', '')
        environ['PATH_INFO'] = path[len(self.base_path):]
        environ['SCRIPT_NAME'] = self.base_path
        return self.application(environ, start_response)


class TracEnvironMiddleware(object):

    def __init__(self, application, env_parent_dir, env_paths, single_env):
        self.application = application
        self.environ = {}
        self.environ['trac.env_path'] = None
        if env_parent_dir:
            self.environ['trac.env_parent_dir'] = env_parent_dir
        elif single_env:
            self.environ['trac.env_path'] = env_paths[0]
        else:
            self.environ['trac.env_paths'] = env_paths

    def __call__(self, environ, start_response):
        for k,v in self.environ.iteritems():
            environ.setdefault(k, v)
        return self.application(environ, start_response)


if gottrac:
    class TracHTTPServer(ThreadingMixIn, WSGIServer):

        def __init__(self, server_address, application, env_parent_dir, env_paths):
            WSGIServer.__init__(self, server_address, application,
                            request_handler=TracHTTPRequestHandler)


    class TracHTTPRequestHandler(WSGIRequestHandler):

        server_version = 'tracd/' + VERSION

        def address_string(self):
            # Disable reverse name lookups
            return self.client_address[:2][0]

stop = False
httpd = None

def main(startstring):
    if not gottrac:
        rlog(100, 'tracserver', 'trac is not installed')
        return
    global httpd
    from optparse import OptionParser, OptionValueError
    parser = OptionParser(usage='usage: %prog [options] [projenv] ...',
                          version='%%prog %s' % VERSION)
    auths = {}
    def _auth_callback(option, opt_str, value, parser, cls):
        info = value.split(',', 3)
        if len(info) != 3:
            raise OptionValueError("Incorrect number of parameters for %s"
                                   % option)

        env_name, filename, realm = info
        auths[env_name] = cls(os.path.abspath(filename), realm)

    def _validate_callback(option, opt_str, value, parser, valid_values):
        if value not in valid_values:
            raise OptionValueError('%s must be one of: %s, not %s'
                                   % (opt_str, '|'.join(valid_values), value))
        setattr(parser.values, option.dest, value)

    parser.add_option('-a', '--auth', action='callback', type='string',
                      metavar='DIGESTAUTH', callback=_auth_callback,
                      callback_args=(DigestAuthentication,),
                      help='[projectdir],[htdigest_file],[realm]')
    parser.add_option('--basic-auth', action='callback', type='string',
                      metavar='BASICAUTH', callback=_auth_callback,
                      callback_args=(BasicAuthentication,),
                      help='[projectdir],[htpasswd_file],[realm]')

    parser.add_option('-p', '--port', action='store', type='int', dest='port',
                      help='the port number to bind to')
    parser.add_option('-b', '--hostname', action='store', dest='hostname',
                      help='the host name or IP address to bind to')
    parser.add_option('--protocol', action='callback', type="string",
                      dest='protocol', callback=_validate_callback,
                      callback_args=(('http', 'scgi', 'ajp', 'fcgi'),),
                      help='http|scgi|ajp|fcgi')
    parser.add_option('-e', '--env-parent-dir', action='store',
                      dest='env_parent_dir', metavar='PARENTDIR',
                      help='parent directory of the project environments')
    parser.add_option('--base-path', action='store', type='string', # XXX call this url_base_path?
                      dest='base_path',
                      help='the initial portion of the request URL\'s "path"')

    parser.add_option('-r', '--auto-reload', action='store_true',
                      dest='autoreload',
                      help='restart automatically when sources are modified')

    parser.add_option('-s', '--single-env', action='store_true',
                      dest='single_env', help='only serve a single '
                      'project without the project list', default=False)

    if os.name == 'posix':
        parser.add_option('-d', '--daemonize', action='store_true',
                          dest='daemonize',
                          help='run in the background as a daemon')
        parser.add_option('--pidfile', action='store',
                          dest='pidfile',
                          help='When daemonizing, file to which to write pid')
        parser.add_option('--umask', action='store', type='int', dest='umask',
                          metavar='MASK',
                          help='When daemonizing, file mode creation mask '
                          'to use (default 022)')

    parser.set_defaults(port=None, hostname='', base_path='', daemonize=False,
                        protocol='http', umask=022)
    options, args = parser.parse_args(startstring.split())
    if not args and not options.env_parent_dir:
        parser.error('either the --env-parent-dir option or at least one '
                     'environment must be specified')
    if options.single_env:
        if options.env_parent_dir:
            parser.error('the --single-env option cannot be used with '
                         '--env-parent-dir')
        elif len(args) > 1:
            parser.error('the --single-env option cannot be used with '
                         'more than one enviroment')
    if options.daemonize and options.autoreload:
        parser.error('the --auto-reload option cannot be used with '
                     '--daemonize')

    if options.port is None:
        options.port = {
            'http': 80,
            'scgi': 4000,
            'ajp': 8009,
            'fcgi': 8000,
        }[options.protocol]
    server_address = (options.hostname, options.port)

    # relative paths don't work when daemonized
    args = [os.path.abspath(a) for a in args]
    if options.env_parent_dir:
        options.env_parent_dir = os.path.abspath(options.env_parent_dir)
    if parser.has_option('pidfile') and options.pidfile:
        options.pidfile = os.path.abspath(options.pidfile)

    wsgi_app = TracEnvironMiddleware(dispatch_request,
                                     options.env_parent_dir, args,
                                     options.single_env)
    if auths:
        if options.single_env:
            project_name = os.path.basename(args[0])
            wsgi_app = AuthenticationMiddleware(wsgi_app, auths, project_name)
        else:
            wsgi_app = AuthenticationMiddleware(wsgi_app, auths)
    base_path = options.base_path.strip('/')
    if base_path:
        wsgi_app = BasePathMiddleware(wsgi_app, base_path)

    try:
        httpd = TracHTTPServer(server_address, wsgi_app,
                                   options.env_parent_dir, args)
    except socket.error, ex:
        if 'already in use' in str(ex):
            rlog(10, 'tserver', 'server is already running')
            return
    rlog(10, 'tserver', 'Server starting in PID %i.' % os.getpid())
    addr, port = server_address
    if not addr or addr == '0.0.0.0':
        rlog(10, 'tserver', 'Serving on 0.0.0.0:%s view at http://127.0.0.1:%s/%s' \
                       % (port, port, base_path))
    else:
        rlog(10, 'tserver', 'Serving on http://%s:%s/%s' % (addr, port, base_path))

    try:
        if options.daemonize:
            daemon.daemonize(pidfile=options.pidfile, progname='tracd',
                             umask=options.umask)

        if options.autoreload:
            def modification_callback(file):
                rlog(10, 'tserver', 'Detected modification of %s, restarting.' \
                                   % file)
            autoreload.main(serve, modification_callback)
        else:
            poll = select.poll()
            poll.register(httpd.socket)
            while not stop:
                try:
                    todo = poll.poll(1000)
                except:
                    continue
                if todo:
                    try:
                        httpd.handle_request()
                    except socket.error, ex:
                        if 'Bad file descriptor' in str(ex):
                            pass
                        else:
                            raise
                    time.sleep(0.001)
            rlog(10, 'tserver', 'stopping')

    except KeyboardInterrupt:
        return

def init():
    if cfg.get('startup'):
        start_new_thread(main, (cfg.get('startup'), ))
        time.sleep(1)

def shutdown():
    global stop
    global httpd
    stop = True
    if httpd:
        try:
            httpd.server_close()
        except socket.error:
            pass
        time.sleep(1)
        httpd = None

def handle_tserverstart(bot, ievent):
    if not gottrac:
        ievent.reply('trac is not installed')
        return
    if not ievent.rest:
        start = "%s --port 10102 -s" % (datadir + os.sep + 'trac')
    else:
        start = ievent.rest
    cfg['startup'] = start
    cfg.save()
    init()
    if httpd:
        ievent.reply('tracserver enabled at http://%s:%s' % httpd.server_address)
    else:
        ievent.reply("can't start server")

cmnds.add('tserver-start', handle_tserverstart, 'OPER', options={'env_parent_dir': datadir + os.sep + 'trac','port' : \
'10102', 'hostname': '', 'base_path': datadir + os.sep + 'trac', 'daemonize': False, 'protocol': \
'http', 'umask': 022 }, threaded=True)
examples.add('tserver-start' , 'start the trac server', 'tserver-start --port 10102 --env gozerdata/trac')

def handle_tserverstop(bot, ievent):
    cfg['startup'] = ""
    cfg.save()
    shutdown()
    if httpd:
        ievent.reply("can't stop server")
    else:
        ievent.reply("server stopped")

cmnds.add('tserver-stop', handle_tserverstop, 'OPER', threaded=True)
examples.add('tserver-stop', 'stop the trac server', 'tserver-stop')
