# gozerbot/utils/locking.py
#
#

""" generic functions """

__copyright__ = 'this file is in the public domain'

from exception import handle_exception
from trace import callstack
import logging, sys

locks = []

def lockdec(lock):
    def locked(func):
        def lockedfunc(*args, **kwargs):
            lock.acquire()
            locks.append(str(func))
            res = None
            try:
                res = func(*args, **kwargs)
            finally:
                lock.release()
                locks.remove(str(func))
            return res
        return lockedfunc
    return locked
