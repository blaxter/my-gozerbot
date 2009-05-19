# gozerbot/aliases.py
#
#

""" command aliases """

__copyright__ = 'this file is in the public domain'


# gozerbot imports
from gozerbot.persist.persist import Persist
from gozerbot.datadir import datadir

# basic import
import os

# the aliases object
aliases = Persist(datadir + os.sep + 'aliases.new', init=False)
if not aliases.data:
    aliases.data = {}

def aliasreverse(what):
    """ get the reverse of an alias. """
    for i, j in aliases.data.iteritems():
        if what == j:
            return i

def aliascheck(ievent):

    """ check if alias is available. """

    try:

        cmnd = ievent.txt.split()[0]
        alias = aliases.data[cmnd]
        ievent.txt = ievent.txt.replace(cmnd, alias, 1)
        ievent.alias = alias
        ievent.aliased = cmnd

    except (IndexError, KeyError):
        pass

def aliassave():

    """ save aliases. """

    aliases.save()

def aliasset(fromm, to):

    """ set an alias. """

    aliases.data[fromm] = to

def aliasdel(fromm):

    """ delete an alias. """

    try:

        del aliases.data[fromm]
        return 1

    except KeyError:
        pass

def aliasget(fromm):

    """ retrieve an alias. """

    if aliases.data.has_key(fromm): 
        return aliases.data[fromm]
