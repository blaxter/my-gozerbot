# web/quotes.py
#
#

""" show all quotes """

__copyright__ = 'this file is in the public domain'


from gozerbot.config import config
from gozerbot.database.db import db
from gozerplugs.webserver.server import httpd

def handle_quotesdb(event):
    """ show all database quotes """
    result = []
    dbresult = db.execute(""" SELECT indx, quote FROM quotes """)
    if not dbresult:
        return ['no quotes', ]
    for i in dbresult:
        result.append("[%s] %s" % (i[0], i[1]))
    return result

if httpd:
    httpd.addhandler('/quotes', handle_quotesdb)
