# plugs/mailexceptions.py
#
#

""" mail exceptions in backlog """

__copyright__ = 'this file is in the public domain'

from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.generic import exceptionlist
from gozerbot.plughelp import plughelp
import smtplib

plughelp.add('mailexceptions', 'mail list of occured exceptions to \
bart@gozerbot.org')

def handle_mailexceptions(bot, ievent):
    """ mailexceptions [<email>] .. mail exceptions in log """
    if not len(exceptionlist):
        ievent.reply("no exceptions available")
        return   
    try:
        mailto = ievent.args[0]
    except IndexError:
        mailto = 'bart@gozerbot.org'
    try:
        mailserver = mailto.split('@')[1]
    except IndexError:
        ievent.reply("can't determine mailserver from %s" % mailto)
        return
    fromaddr = 'gozerbot@localhost'
    msg = ("From: %s\r\nTo: %s\r\n\r\n"
       % (fromaddr, mailto))
    for i in exceptionlist:
        msg += "+++ %s\r\n" % i 
    server = smtplib.SMTP(mailserver)
    server.sendmail(fromaddr, mailto, msg)
    ievent.reply("%s exceptions send to %s" % (len(exceptionlist), mailto))

cmnds.add('mailexceptions', handle_mailexceptions, 'OPER')
examples.add('mailexceptions' , 'mailexceptions [<email>] .. mail exceptions \
log to bart@gozerbot.org or to provided email', '1) mailexceptions 2) \
mailexception mekker@miep')
