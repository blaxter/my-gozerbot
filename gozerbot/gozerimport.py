# gozerbot/myimport.py
#
#

""" use the imp module to import modules. """

__copyright__ = 'this file is in the public domain'

# gozerbot import 
from generic import rlog

# basic import
import time, sys, imp, os

def gozer_import(name, path=None):

    """ import module <name> with the imp module  .. will reload module is already in sys.modules. """

    rlog(0, 'gozerimport', 'importing %s' % name)
    splitted = name.split('.')

    for plug in splitted:
        fp, pathname, description = imp.find_module(plug, path)
        try:
           result = imp.load_module(plug, fp, pathname, description)
           try:
               path = result.__path__
           except:
               pass
        finally:
            if fp:
                fp.close()

    return result

def force_import(name):

    """ force import of module <name> by replacing it in sys.modules. """

    plug = gozer_import(name)
    sys.modules[name] = plug
    return plug
