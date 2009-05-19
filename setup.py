#!/usr/bin/env python
#
#

__copyright__ = 'this file is in the public domain'
__revision__ = '$Id: setup.py 71 2005-11-10 13:37:50Z bart $'

from setuptools import setup

setup(
    name='gozerbot',
    version='0.9.0.15',
    url='http://gozerbot.org',
    author='Bart Thate',
    author_email='bthate@gmail.com',
    description='the irc bot and jabber bot in one',
    license='BSD',
    scripts = ['bin/gozerbot', 'bin/gozerbot-init', 'bin/gozerbot-start', 'bin/gozerbot-stop', 'bin/gozerbot-upgrade', 'bin/gozerbot-udp', 'bin/gozerbot-install', 'bin/gozerbot-nest'],
    packages=['gozerbot', 'gozerbot.contrib','gozerbot.rest', \
'gozerbot.persist', 'gozerbot.utils', 'gozerbot.irc', 'gozerbot.jabber', \
'gozerbot.plugs', 'gozerbot.compat', 'gozerbot.threads', 'gozerbot.database'],
    install_requires = ['sqlalchemy >= 0.5.0',
        'pytz >= 1.0',
        'simplejson >= 1.0',
        'feedparser >= 1.0',
        'xmpppy >= 0.4', 
        'pydns >=  2.3.3'],
    long_description = """
    GOZERBOT features:

    * provide both IRC and Jabber support
    * user management by userhost .. bot will not respond if it doesn't know you (see USER)
    * fleet .. use more than one bot in a program (list of bots) (see FLEET)
    * use the bot through dcc chat
    * fetch rss feeds (see RSS)
    * remember items
    * relaying between bots (see RELAY)
    * program your own plugins (see PROGRAMPLUGIN)
    * query other bots with json REST (see CLOUD)
    * serve as a udp <-> irc or jabber notification bot (see UDP
    * sqlalchemy support
    * 100+ plugins
"""
)
