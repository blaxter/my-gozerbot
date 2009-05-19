#!/usr/bin/env python
#
# $Id: svnlog.py 341 2006-03-08 21:28:13Z bart $
#
# edit config section and ..
# edit the udp section in botdir/data/config if it's not there see 
# examples/config. put this script in your svn repro/hooks dir and ..
# add /full/path/to/svnlog.py  --repository "$REPOS" --revision "$REV" 
# to post-commit. this script expects stuf in /usr/local/bin

__copyright__ = 'this file is in the public domain'

# config
host = 'localhost'
port = 5500
passwd = 'mekker'
channel = '#dunkbots'
lookcmnd = '/usr/local/bin/svnlook'
# end config

import socket, os, sys, getopt, commands

try:
    a2 = getopt.gnu_getopt(sys.argv[1:], "", ['repository', 'revision'])
    repro = a2[1][0]
    rev = a2[1][1]
    a = commands.getoutput('%s changed %s' % (lookcmnd, repro))
    b = commands.getoutput('%s log %s' % (lookcmnd, repro)).strip()
    l = []
    for i in a.split()[1::2]:
        l.append(i.strip())
    aaa = ' '.join(l)
    who = os.getlogin()
    z = '%s %s %s (%s) who: %s log: "%s" files: %s' % \
(passwd, channel, repro, rev, who, b, aaa)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(z, (host, port))
    except Exception, v:
        print "can't send " + z + ' ' + str(v)
        pass
except Exception, ex:
    print ex
