# web/karma.py
#
#

""" show all karma items """

__copyright__ = 'this file is in the public domain'

from gozerbot.config import config
from gozerbot.database.db import db
from gozerplugs.webserver.server import httpd

def handle_karmadb(event):
    """ show all database karma items """
    result = []
    dbresult = db.execute(""" SELECT item, value FROM karma ORDER BY \
value DESC""")
    if not dbresult:
        return ['no karma items', ]
    for i in dbresult:
        result.append("%s = %s" % (i[0], i[1]))
    return result

if httpd:
    httpd.addhandler('/karma', handle_karmadb)
