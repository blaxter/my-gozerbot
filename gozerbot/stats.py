# gozerbot/stats.py
#
#

""" maintain per session stats. """

from gozerbot.utils.statdict import Statdict

class GozerStats(object):

    """ dict containing all gozerbot related stats. """

    def __init__(self):
        self.data = {}

    def init(self, item):

        """ initialize a stats item. """

        self.data[item] = Statdict()

    def up(self, item, issue):

        """ up a stats item. """

        if not self.data.has_key(item):
            self.init(item)
        self.data[item].upitem(issue)

    def get(self, item):

        """ return stats item. """

        try:
            return self.data[item]
        except KeyError:
            return 

    def list(self, item):

        """ list all stats belonging to item. """

        if self.data.has_key(item):
            return self.data[item].keys()

    def all(self):

        """ list all stats items. """

        return self.data.keys()

# the gozerbot stats object
stats = GozerStats()
