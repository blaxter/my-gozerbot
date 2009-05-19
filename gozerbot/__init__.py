# gozerbot package
#
#

""" register all .py files """

__copyright__ = 'this file is in the public domain'

import os
import exit

(f, tail) = os.path.split(__file__)
__all__ = []

for i in os.listdir(f):
    if i.endswith('.py'):
        __all__.append(i[:-3])
    elif os.path.isfile('gozerbot' + os.sep + i + os.sep + '__init__.py'):
         __all__.append(i)
__all__.remove('__init__')

del f, tail
