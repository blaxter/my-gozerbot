# gozerbot/utils/trace.py
#
#

""" trace related functions """

__copyright__ = 'this file is in the public domain'

import sys, os

def calledfrom(frame):
    try:
        plugname = frame.f_back.f_code.co_filename
        name = plugname.split(os.sep)[-1][:-3]
        if name == '__init__':
            name = plugname.split(os.sep)[-2]
        if name == 'generic':
            plugname = frame.f_back.f_back.f_code.co_filename
            name = plugname.split(os.sep)[-1][:-3]
    except AttributeError:
        name = None
    del frame
    return name

def callstack(frame):
    result = []
    loopframe = frame
    while 1:
        try:
            plugname = loopframe.f_back.f_code.co_filename
            result.append("%s:%s" % (plugname.split(os.sep)[-1][:-3], \
loopframe.f_back.f_lineno))
            loopframe = loopframe.f_back
        except:
            break
    del frame
    return result

def whichmodule(depth=1):
    try:
        frame = sys._getframe(depth)
        plugfile = frame.f_back.f_code.co_filename[:-3].split('/')
        lineno = frame.f_back.f_lineno
        mod = []
        for i in plugfile[::-1]:
            mod.append(i)
            if i == 'gozerbot' or i == 'gozerplugs':
                break
        modstr = '.'.join(mod[::-1]) + ':' + str(lineno)
    except AttributeError:
        modstr = None
    del frame
    return modstr
