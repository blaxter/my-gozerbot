# gozerbot/ignore.py
#
#

""" ignore module. """

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from persist.persist import Persist
from datadir import datadir
from periodical import interval

# basic imports
import time, os, thread

ignore = {}
timeset = {}

def addignore(userhost, ttime):

    """ add ignore based on userhost .. record time when ignore is set. """

    ignore[userhost] = int(ttime)
    timeset[userhost] = time.time()
    
def delignore(userhost):

    """ remove ignore. """

    try:
        del ignore[userhost]
        del timeset[userhost]
        return 1
    except KeyError:
        return 0

def shouldignore(userhost):

    """ check if we should ignore. """

    try:
        ignoretime = ignore[userhost]
        ignoreset = timeset[userhost]
    except KeyError:
        return 0

    if time.time() - ignoretime < ignoreset:
        return 1

    return 0


@interval(60)
def ignorecheck():

    """ periodic function to remove users that no longer need to be ignored. """

    for userhost in ignore.keys():
        if not shouldignore(userhost):
            delignore(userhost)

# first call to trigger interval
ignorecheck()
