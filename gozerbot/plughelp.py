# gozerbot/plughelp.py
#
#

""" help about plugins. """

__copyright__ = 'this file is in the public domain'

class Plughelp(dict):

    """ dict holding plugins help string. """ 

    def add(self, item, descr):

        """ add plugin help string. """

        item = item.lower()
        self[item] = descr

    def get(self, item):

        """ get plugin help string. """

        item = item.lower()
        try:
            return self[item]
        except KeyError:
            return None

# plughelp object
plughelp = Plughelp()
