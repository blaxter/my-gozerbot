# plugs/alias.py
#
#

""" this alias plugin allows aliases for commands to be added. aliases are in
 the form of <alias> -> <command> .. aliases to aliases are not allowed
"""

__copyright__ = 'this file is in the public domain'

# gozerbot imports
from gozerbot.aliases import aliasget, aliasdel, aliasset, aliases
from gozerbot.tests import tests
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
from gozerbot.datadir import datadir
from gozerbot.utils.generic import convertpickle

# basuc imports
import os

plughelp.add('alias', 'support for aliases')

## UPGRADE PART

def upgrade():

    """ upgrade the aliases pickle file to to aliases.new json file. """

    convertpickle(datadir + os.sep + 'aliases', datadir + os.sep + \
'aliases.new')

## END UPGRADE PART

def handle_aliassearch(bot, ievent):

    """ alias-search <what> .. search aliases. """

    try:
        what = ievent.args[0]
    except IndexError:
        ievent.missing('<what>')
        return

    result = []
    res = []

    for i, j in aliases.data.iteritems():
        if what in i or what in j:
            result.append((i, j))

    if not result:
        ievent.reply('no %s found' % what)
    else:
        for i in result:
            res.append("%s => %s" % i)
        ievent.reply("aliases matching %s: " % what, res, dot=True)

cmnds.add('alias-search', handle_aliassearch, 'USER')
examples.add('alias-search', 'search aliases',' alias-search web')
tests.add('alias-set mekker miep').add('alias-search mekker', 'miep').add('alias-del mekker')

def handle_aliasset(bot, ievent):

    """ alias-set <from> <to> .. set alias. """

    global aliases

    try:
        (aliasfrom, aliasto) = (ievent.args[0], ' '.join(ievent.args[1:]))
    except IndexError:
        ievent.missing('<from> <to>')
        return

    if not aliasto:
        ievent.missing('<from> <to>')
        return

    if aliases.data.has_key(aliasto):
        ievent.reply("can't alias an alias")
        return

    if cmnds.has_key(aliasfrom):
        ievent.reply('command with same name already exists.')
        return

    # add alias and save
    aliasset(aliasfrom, aliasto)
    aliases.save()
    ievent.reply('alias added')

cmnds.add('alias-set', handle_aliasset, 'OPER', allowqueue=False)
examples.add('alias-set', 'alias-set <alias> <command> .. define alias', \
'alias-set ll list')
aliases.data['alias'] = 'alias-set'
tests.add('alias-set mekker2 list', 'alias added').add('mekker2', 'grep').add('alias-del mekker2')

def handle_delalias(bot, ievent):

    """ alias-del <word> .. delete alias. """

    try:
        what = ievent.args[0]
    except IndexError:
        ievent.missing('<what>')
        return

    # del alias and save
    if not aliasdel(what):
        ievent.reply('there is no %s alias' % what)
        return

    aliases.save()
    ievent.reply('alias deleted')

cmnds.add('alias-del', handle_delalias, 'OPER')
examples.add('alias-del', 'alias-del <what> .. delete alias', 'alias-del ll')
tests.add('alias-set mekker3 miep').add('alias-del mekker3', 'alias deleted')

def handle_getalias(bot, ievent):

    """ alias-get <word> .. show alias. """

    try:
        what = ievent.args[0]
    except IndexError:
        ievent.missing('<what>')
        return
    # del alias and save

    alias = aliasget(what)

    if not alias:
        ievent.reply('there is no %s alias' % what)
        return

    ievent.reply(alias)

cmnds.add('alias-get', handle_getalias, 'USER')
examples.add('alias-get', 'alias-get <what> .. get alias', 'alias-get v')
tests.add('alias-set mekker4 miep').add('alias-get mekker4', 'miep').add('alias-del mekker4')

def init():

     """ initialise the alias plugin. """

     aliases.init()
