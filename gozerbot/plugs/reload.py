# plugs/reload.py
#
#

__copyright__ = 'this file is in the public domain'

from gozerbot.config import config
from gozerbot.plugins import plugins
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
from gozerbot.aliases import aliases
from gozerbot.gozerimport import gozer_import
from gozerbot.tests import tests
import os, sets

plughelp.add('reload', 'reload a plugin')

def handle_reload(bot, ievent):
    """ reload <plugin> .. reload a plugin """
    try:
        plugs = ievent.args
    except IndexError:
        ievent.missing('<list plugins>')
        return
    reloaded = []
    errors = []
    for plug in plugs:
        plug = plug.lower()
        if plug == 'config':
            config.reload()
            ievent.reply('config reloaded')
            continue
        p = gozer_import('gozerbot.plugs.__init__')
        if plug in p.__plugs__:
            reloaded.extend(plugins.reload('gozerbot.plugs', plug))
            continue
        try:
            reloaded.extend(plugins.reload('myplugs', plug))
        except ImportError, ex:
            try:
                reloaded.extend(plugins.reload('gozerplugs', plug))
            except ImportError, ex:
                errors.append(str(ex))
    ievent.reply('reloaded: ', reloaded, dot=True)
    try:
       cantreload = list(sets.Set(plugs) - sets.Set(reloaded))
       if cantreload:
           ievent.reply("can't reload: " , cantreload, dot=True)
           if errors:
               ievent.reply('errors: ', errors)
    except AttributeError:  # in case of !reload reload
       pass 
    
cmnds.add('reload', handle_reload, 'OPER')
examples.add('reload', 'reload <plugin>', 'reload core')
aliases.data['load'] = 'reload'
tests.add('reload country', 'country').add('unload country')

def handle_unload(bot, ievent):
    """ unload <plugin> .. unload a plugin """
    try:
        what = ievent.args[0].lower()
    except IndexError:
        ievent.missing('<plugin>')
        return
    if not plugins.exist(what):
        ievent.reply('there is no %s module' % what)
        return
    got = plugins.unload(what)
    for what in got:
        plugins.disable(what)
    ievent.reply("unloaded and disabled: ", got, dot=True)

cmnds.add('unload', handle_unload, 'OPER')
examples.add('unload', 'unload <plugin>', 'unload relay')
tests.add('reload country').add('unload country', 'country')
