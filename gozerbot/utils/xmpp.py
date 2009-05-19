# gozerbot/utils/xmpp.py
#
#

from xml.etree import cElementTree as ET
import types

def make_presence(xml):
    pres = {'subject': '', 'to': '', 'message': '', 'name': '', 'resource': '', 'jid': ''}
    if type(xml) == types.DictType:
        pres.update(xml)
        return pres
    et = ET.XMLID(xml)
    pres.update(et[0].items())
    xml = ET.XML(xml)
    try:
        pres['name'] = pres['from'].split('@')[0]
        pres['resource'] = pres['from'].split('/')[1]
        pres['jid'] = pres['from'].split('/')[0]
    except KeyError:
        pass
    return pres

def make_message(xml):
    msg = {'subject': '', 'to': '', 'txt': '', 'message': '', 'from': '', 'jid': '', 'name': '', 'resource': ''}
    if type(xml) == types.DictType:
        msg.update(xml)
        return msg
    et = ET.XMLID(xml)
    msg.update(et[0].items())
    xml = ET.XML(xml)
    msg['message'] = unicode(xml.findtext('body'))
    msg['name'] = msg['from'].split('@')[0]
    msg['resource'] = msg['from'].split('/')[1]
    msg['jid'] = msg['from'].split('/')[0]
    return msg
