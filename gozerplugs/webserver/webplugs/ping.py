# web/ping.py
#
#

""" return pong """

__copyright__ = 'this file is in the public domain'

from gozerplugs.webserver.server import httpd

def handle_ping(event):
    """ return pong """
    return ['pong', ]

if httpd:
    httpd.addhandler('/ping', handle_ping)
