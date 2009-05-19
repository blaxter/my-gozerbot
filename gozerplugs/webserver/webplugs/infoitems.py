# web/infoitems.py
#
#

""" show all infoitems """

__copyright__ = 'this file is in the public domain'

from gozerbot.config import config
from gozerbot.database.db import db
from gozerplugs.webserver.server import httpd

def handle_infoitemsdb(event):
    """ show database pickle items """
    dbresult = db.execute(""" SELECT item, description FROM infoitems """)
    if not dbresult:
        return ['no infoitems', ]
    resultdict = {}
    result = []
    for i in dbresult:
        if not resultdict.has_key(i[0]):
            resultdict[i[0]] = [i[1], ]
        else:
            resultdict[i[0]].append(i[1])
    for i, j in resultdict.iteritems():
        result.append("%s ==> %s" % (i, ' .. '.join(j)))
    return result

if httpd:
    httpd.addhandler('/infoitems', handle_infoitemsdb)
