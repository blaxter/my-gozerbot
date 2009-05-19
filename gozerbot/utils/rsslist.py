# gozerbot/rsslist.py
#
#

""" create a list of rss data """

__copyright__ = 'this file is in the public domain'

from exception import handle_exception
import xml.dom.minidom

def gettext(nodelist):
    """ get text data from nodelist """
    result = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE or node.nodeType == \
node.CDATA_SECTION_NODE:
            stripped = node.data.strip()
            if stripped:
                result += stripped
    return result

def makersslist(xlist, nodes , d={}):
    """ recurse until txt is found """
    for i in nodes:
        if i.nodeType == i.ELEMENT_NODE:
            dd = d[i.nodeName] = {}
            makersslist(xlist, i.childNodes, dd)
            if dd:
                xlist.append(dd)
        txt = gettext(i.childNodes)
        if txt:
            d[i.nodeName] = txt
        
def rsslist(txt):
    """ create list of dictionaries with rss data """
    dom = xml.dom.minidom.parseString(txt)
    result = []
    makersslist(result, dom.childNodes)
    return result
