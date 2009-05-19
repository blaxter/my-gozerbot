# gozerbot/utils/exception.py
#
#

""" generic functions """

__copyright__ = 'this file is in the public domain'

exceptionlist = []

directlist = ['urlopen error timed out', '[Errno socket error] timed out', \
'Name or service not known', 'No route to host', 'Non-recoverable failure in \
name resolution']

from gozerbot.utils.log import rlog
import sys, traceback, logging

def exceptionmsg():
    exctype, excvalue, tb = sys.exc_info()
    trace = traceback.extract_tb(tb)
    result = ""
    for i in trace:
        fname = i[0]
        linenr = i[1]
        func = i[2]
        result += "%s:%s %s | " % (fname, linenr, func)
    del trace
    return "%s%s: %s" % (result, exctype, excvalue)

def handle_exception(event=None, log=True, short=False, txt=""):
    errormsg = exceptionmsg()
    #logging.error(errormsg)
    if log:
        rlog(1000, 'EXCEPTION', errormsg)
    if event:
        event.reply(errormsg)
