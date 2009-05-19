#!/usr/bin/env python
#
#

from gozerbot.datadir import datadir
from gozerbot.db import db
import os

print "ADDING USERS"

from gozerbot.users import Users
u = Users(datadir + os.sep + 'users')
for i in u.data:
    for j in i.userhosts:
        print i.name, j
        try:
            db.execute(""" INSERT INTO userhosts(userhost, name) \
VALUES(%s, %s)  """, (j, i.name))
        except Exception, ex:
            print ex            
    for j in i.perms:
        print i.name, j
        try:
            db.execute(""" INSERT INTO perms(name, perm) \
VALUES(%s, %s)  """, (i.name, j))
        except Exception, ex:
            print ex            
    if i.email:
        print i.name, i.email
        try:
            db.execute(""" INSERT INTO email(name, email) \
VALUES(%s, %s)  """, (i.name, i.email))
        except Exception, ex:
            print ex            
    for j in i.permit:
        print i.name, j
        try:
            db.execute(""" INSERT INTO permits(name, permit) \
VALUES(%s, %s)  """, (i.name, j))
        except Exception, ex:
            print ex            
    for j in i.status:
        print i.name, j
        try:
            db.execute(""" INSERT INTO statuses(name, status) \
VALUES(%s, %s)  """, (i.name, j))
        except Exception, ex:
            print ex            
    if i.passwd:
        print i.name, i.passwd
        try:
            db.execute(""" INSERT INTO passwords(name, passwd) \
VALUES(%s, %s)  """, (i.name, i.passwd))
        except Exception, ex:
            print ex            

from gozerplugs.plugs.infoitem import Infoitems
info = Infoitems(datadir + os.sep + 'infoitems')

print "ADDING INFOITEMS"

if info.data:

    for i,j in info.data.iteritems():
        for z in j:
            print i, z
            try:
                db.execute(""" INSERT INTO infoitems(item, description, \
userhost, time) VALUES(%s, %s, %s, %s)  """, (i, z, '', 0))
            except Exception, ex:
                print ex            

print "ADDING KARMA"

from gozerplugs.plugs.karma import Karma
k = Karma(datadir)

if k.karma:

    for i,j in k.karma.iteritems():
        print i, j
        try:
            db.execute(""" INSERT INTO karma(item, value) VALUES(%s, %s)  """, \
(i, j))
        except Exception, ex:
            print ex            

for i,j in k.reasonup.iteritems():
    for z in j:
        print i, z
        try:
            db.execute(""" INSERT INTO whykarma(item, updown, why) \
VALUES(%s, %s, %s)  """, (i, 'up', z))
        except Exception, ex:
            print ex            

for i,j in k.reasondown.iteritems():
    for z in j:
        print i, z
        try:
            db.execute(""" INSERT INTO whykarma(item, updown, why) \
VALUES(%s, %s, %s)  """, (i, 'down', z))
        except Exception, ex:
            print ex            

for i,j in k.whodown.iteritems():
    for z in j:
        print i, z
        try:
            db.execute(""" INSERT INTO whokarma(item, nick, updown) \
VALUES(%s, %s, %s)  """, (i, z, 'down'))
        except Exception, ex:
            print ex            

for i,j in k.whoup.iteritems():
    for z in j:
        print i, z
        try:
            db.execute(""" INSERT INTO whokarma(item, nick, updown) \
VALUES(%s, %s, %s)  """, (i, z, 'up'))
        except Exception, ex:
            print ex            

print "ADDING QUOTES"

from gozerplugs.plugs.quote import Quotes
q = Quotes(datadir + os.sep + 'quotes')

for i in q.data:
    print i.txt, i.nick, i.userhost, i.time
    try:
        db.execute(""" INSERT INTO quotes(quote, userhost, createtime, \
nick) VALUES (%s, %s, %s, %s) """, (i.txt, i.userhost, i.time, i.nick))
    except Exception, ex:
        print ex            

print "ADDING TODO"

from gozerplugs.plugs.todo import Todo
todo = Todo(datadir + os.sep + 'todo')

if todo.data:

    for i, j in todo.data.iteritems():
        for z in j:
            print i, z
            try:
                db.execute(""" INSERT INTO todo(name, time, duration, \
warnsec, descr, priority) VALUES(%s, %s, %s, %s, %s, %s) """, \
(z.name, z.time, z.duration, z.warnsec, z.descr, z.priority))
            except Exception, ex:
                print ex            

print 'ADDING LISTS'

from gozerbot.persist import Persist
mylists = Persist(datadir + os.sep + 'mylists')

if mylists.data:

    for i, j in mylists.data.iteritems(): 
        for z, zz in j.iteritems():
            for x in zz:
                print i, z, x
                try:
                    db.execute(""" INSERT INTO list(username, listname, item) \
VALUES(%s, %s, %s) """, (i, z, x))
                except Exception, ex:
                    print ex            


from gozerbot.pdol import Pdol
lists = Pdol(datadir + os.sep + 'lists')

if lists.data:

    for i, j in lists.data.iteritems(): 
        for z in j:
            print i, z
            try:
                db.execute(""" INSERT INTO list(username, listname, item) \
VALUES(%s, %s, %s) """, ('all', i, z))
            except Exception, ex:
                print ex            

print "DONE"
