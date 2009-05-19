# gozerbot/less.py
#
#

""" maintain bot output cache. """

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from utils.limlist import Limlist

class Less(object):

    """ output cache """

    def __init__(self, nr):
        self.data = {}
        self.index = {}
        self.nr = nr

    def add(self, nick, listoftxt):

        """ add listoftxt to nick's output .. set index for used by more 
            commands """

        nick = nick.lower()

        # see if we already have cached output .. if not create limited list
        if not self.data.has_key(nick):
            self.data[nick] = Limlist(self.nr)

        # add data
        self.data[nick].insert(0, listoftxt)
        self.index[nick] = 1

    def get(self, nick, index1, index2):

        """ return less entry. """

        nick = nick.lower()

        try:
            txt = self.data[nick][index1][index2]
        except (KeyError, IndexError):
            txt = None
        return txt

    def more(self, nick, index1):

        """ return more entry pointed to by index .. increase index """

        nick = nick.lower()

        try:
            nr = self.index[nick]
        except KeyError:
            nr = 1

        try:
            txt = self.data[nick][index1][nr]
            size = len(self.data[nick][index1])-nr
            self.index[nick] = nr+1
        except (KeyError, IndexError):
            txt = None
            size = 0

        return (txt, size-1)

    def size(self, nick):

        """ return sizes of cached output. """

        nick = nick.lower()
        sizes = []

        if not self.data.has_key(nick):
            return sizes

        for i in self.data[nick]:
            sizes.append(len(i))

        return sizes
