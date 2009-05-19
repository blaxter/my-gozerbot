# gozerbot/morphs.py
#
#

""" convert input/output stream. """

# gozerbot imports
from utils.exception import handle_exception
from utils.trace import calledfrom

# basic imports
import sys

class Morph(object):

    """ transform stream. """

    def __init__(self, func):
        self.plugname = calledfrom(sys._getframe(1))
        self.func = func

    def do(self, *args, **kwargs):

        """ do the morphing. """

        try:
            return self.func(*args, **kwargs)
        except Exception, ex:
            handle_exception()

class MorphList(list):

    """ list of morphs. """

    def add(self, func, index=None):

        """ add moprh. """

        if not index:
            self.append(Morph(func))
        else:
            self.insert(index, Moprh(func))

        return self

    def do(self, input, *args, **kwargs):

        """ call morphing chain. """

        for morph in self:
            input = morph.do(input, *args, **kwargs) or input

        return input

    def unload(self, plugname):

        """ unload morhps belonging to plug <plugname>. """

        for index in range(len(self)-1, -1, -1):
            if self[index].plugname == plugname:
                del self[index]

# moprhs used on input
inputmorphs = MorphList()

# morphs used on output
outputmorphs = MorphList()
