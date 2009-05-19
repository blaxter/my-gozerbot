# gozerbot package
#
#

""" register all .py files """

__copyright__ = 'this file is in the public domain'

import os

(f, tail) = os.path.split(__file__)
__all__ = []

for i in os.listdir(f):
    if i.endswith('.py'):
        __all__.append(i[:-3])
__all__.remove('__init__')

del f, tail
