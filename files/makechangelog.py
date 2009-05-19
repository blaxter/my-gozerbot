#!/usr/bin/env python
#
#

import os

data = os.popen('hg log').readlines()

rev = ""
summary = ""
date = ""
for i in data:
    if i.startswith('changeset'):
        rev = i.split()[1].split(':')[0].strip()
    if i.startswith('date'):
        date = ' '.join(i.split(' ', 1)[1].split()[1:5])
    if i.startswith('summary'):
        summary = i.split(' ', 1)[1].strip()
        if summary.startswith('merge') or summary.startswith('branch merge'):
            summary = ""
            continue
    if rev and summary and data:
        if 'Added tag' in summary:
            print '\n%s' % summary.split()[2]
            print '~' * len(summary.split()[2]) + '\n\n'
        print "%s %s .. %s\n" % (rev, date, summary)
        date = rev = summary = ""

