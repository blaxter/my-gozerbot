# gozerbot/utils/lazydict.py
#
# thnx to maze

""" a lazydict allows dotted access to a dict .. dict.key """

class LazyDict(dict):

    """ Lazy dict allows dotted access to a dict """


    def __getattr__(self, attr, default={}):

        """ get attribute .. if not available init to default. """

        if not self.has_key(attr):
            self[attr] = default

        return self[attr]

    def __setattr__(self, attr, value):

        """ set attribute. """

        self[attr] = value

    def __str__(self):

        """ return a string representation of the dict """

        res = ""

        for item, value in self.iteritems():
            res += "%s = %s " % (unicode(item), unicode(value))

        return res
