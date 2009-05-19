# gozerbot/utils/log.py
#
#

""" gozerbots logging module. logging is implemented with the use of a 
    loglevel and a loglist of plugins to log for. 
"""

# basic imports
import logging, logging.handlers, sys, traceback, os

# make sure dirs are there
if not os.path.isdir('logs'):
    os.mkdir('logs')
if not os.path.isdir('logs' + os.sep + 'bot'):
    os.mkdir('logs' + os.sep + 'bot')

# the vars
loglevel = 10
logcallbacks = []
loglist = []
logfile = None

# basic logger
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] (%(name)s) %(message)s")

# add logging to file
filehandler = logging.handlers.TimedRotatingFileHandler(
              'logs' + os.sep + 'bot' + os.sep + 'gozerbot.log', 'midnight')
formatter = logging.Formatter("[%(asctime)s] (%(name)s) %(message)s")
filehandler.setFormatter(formatter)
basiclogger = logging.getLogger('')
basiclogger.addHandler(filehandler)

def exceptionmsg():
    """ create a exception traceback as 1 liner. """
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

def rlog(level, descr, txt):
    """ log an item showing description and txt. call logcallbacks if 
        available
    """
    logger = logging.getLogger(descr)
    if level >= loglevel or (loglist and descr in loglist):
        logger.info(txt)
        for cb in logcallbacks:
            try:
                cb(level, descr, txt)
            except:
                print exceptionmsg()

def enable_logging(level=10, list=[]):
    """ enable logging setting loglevel and/ort loglist """
    global loglevel, loglist
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(name)s %(message)s")
    loglevel = level
    loglist = list
