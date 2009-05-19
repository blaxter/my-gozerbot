# gozerbot/examples.py
#
#

""" examples is a dict of example objects. """

__copyright__ = 'this file is in the public domain'

# basic imports
import re

class Example(object):

    """ an example. """

    def __init__(self, descr, ex):
        self.descr = descr
        self.example = ex

class Examples(dict):

    """ examples object is a dict. """

    def add(self, name, descr, ex):

        """ add description and example. """

        self[name.lower()] = Example(descr, ex)

    def size(self):
 
        """ return size of examples dict. """

        return len(self.keys())

    def getexamples(self):

        """ get all examples in list. """

        result = []
        for i in self.values():
            ex = i.example.lower()
            exampleslist = re.split('\d\)', ex)
            for example in exampleslist:
                if example:
                    result.append(example.strip())
        return result

    def getexamplesplug(self):

        """ get all examples in list. """

        result = []
        for i in self.values():
            ex = i.example.lower()
            exampleslist = re.split('\d\)', ex)
            for example in exampleslist:
                if example:
                    result.append(example.strip())
        return result

# main examples object
examples = Examples()
