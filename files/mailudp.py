#!/usr/bin/env python
#
#
# copy this to your home dir and make a .forward file like this:
# (bart@r8):~
# $ cat .forward
# \bart
# "|~/mailudp.py"
#
# edit config vars below to match your bot's config

__copyright__ = 'this file is in the public domain'

import socket, sys, re

# config
host = 'gozerbot.org'
port = 5600
passwd = 'mekker'
printto = 'dunk_'
# end config

def out(what):
    z = '%s %s %s' % (passwd, printto, what)
    z = z[:400]
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(z, (host, port))

fromre = re.compile('^From: (.*)\n', re.M)
subjectre = re.compile('^Subject: (.*)\n', re.M)

frm = ""
subject = ""

a = sys.stdin.readlines()

for i in a:
    try:
        b = fromre.search(i)
        if b:
            frm = b.group(0).strip()
        c = subjectre.search(i)
        if c:
            subject = c.group(0).strip()
        if frm and subject:
            break
    except Exception:
        pass

if frm and subject:
    result = "%s %s" % (frm, subject)
    out(result)
