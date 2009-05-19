# gozerbot/datadir.py
# -*- coding: utf-8 -*-
#

""" pointer to the bot's datadir .. plugs code to init this data dir. """

__copyright__ = 'this file is in the public domain'

# basic imports
import re, os

datadir = 'gozerdata'

def makedirs(ddir=None):

    """ make subdirs in datadir. """

    ddir = ddir or datadir
    curdir = os.getcwd()

    if not os.path.isdir(ddir):
        os.mkdir(ddir)
    if not os.path.isdir(ddir + '/users/'):
        os.mkdir(ddir + '/users/')
    if not os.path.isdir(ddir + '/db/'):
        os.mkdir(ddir + '/db/')
    if not os.path.isdir(ddir + '/fleet/'):
        os.mkdir(ddir + '/fleet/')
    if not os.path.isdir(ddir + '/pgp/'):
        os.mkdir(ddir + '/pgp/')
    if not os.path.isdir(ddir + '/plugs/'):
        os.mkdir(ddir + '/plugs/')
    if not os.path.isdir(ddir + '/old/'):
        os.mkdir(ddir + '/old/')
