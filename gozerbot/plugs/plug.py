# gozerbot/plugs/plug.py
#
#

from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plugins import plugins
from gozerbot.utils.exception import exceptionmsg, handle_exception
from gozerbot.gozerimport import gozer_import 
from gozerbot.tests import tests

def handle_plugenable(bot, ievent):
    doall = False
    if '-a' in ievent.optionset:
        doall = True
    if not ievent.rest and not doall:
        ievent.missing('<plugname>')
        return
    try:
        plugs = gozer_import('gozerplugs').__plugs__
    except ImportError:
        ievent.reply("no gozerplugs package detected")
        return
    if not doall:
        plugs = ievent.rest.split()
    ievent.reply("trying to reload: ", plugs, dot=True)
    errors = []
    reloaded = []
    failed = []
    for plug in plugs:
        try:
            reloaded.extend(plugins.reload('gozerplugs', plug))
        except ImportError, ex:
            errors.append(str(ex))
            failed.append(plug)
        except Exception, ex:
            handle_exception()
            errors.append(exceptionmsg())
            failed.append(plug)
    ievent.reply('enabled plugins: ', reloaded, dot=True)
    if failed:
        ievent.reply('failed to reload: ', failed, dot=True)
    if errors:
        ievent.reply('errors: ', errors, dot=True)
  
cmnds.add('plug-enable', handle_plugenable, 'OPER', options={'-a': ''})
examples.add('plug-enable', 'enable a plugin', 'plug-enable karma')
tests.add('plug-enable country', 'country')

def handle_plugdisable(bot, ievent):
    if not ievent.rest:
        ievent.missing('<plugname>')
        return
    plugs = ievent.rest.split()
    disabled = []
    for plug in plugs:
        plugins.unload(plug)
        plugins.disable(plug)
        disabled.append(plug)
    ievent.reply('disabled plugins: ', disabled)

cmnds.add('plug-disable', handle_plugdisable, 'OPER')
examples.add('plug-disable', 'disable a plugin', 'plug-disable karma')
tests.add('plug-disable country', 'country')

def handle_plugupgrade(bot, ievent):
    alreadygot = []
    upgraded = []
    plugs = []
    if ievent.rest:
        plugs.extend(ievent.rest.split())
    else:
        for name, plug in plugins.plugs.iteritems():
            if hasattr(plug, 'upgrade'):
                plugs.append(name)    
    ievent.reply('starting plugin upgrade for plugins: ', plugs, dot=True)
    errors = []
    for plug in plugs:
        try:
            s = plugins.plugs[plug].size()
        except AttributeError:
            s = 0
        if s and not '-f' in ievent.optionset:
            alreadygot.append(plug)
            continue
        try:
            plugins.plugs[plug].upgrade()
            plugins.reload('gozerplugs', plug)
            ievent.reply('upgraded %s' % plug)
            upgraded.append(plug)
        except AttributeError:
            continue
        except Exception, ex:
            handle_exception()
            errors.append(exceptionmsg())
    if upgraded:
        ievent.reply('upgraded the following plugins: ', upgraded, dot=True)
    if alreadygot:
        ievent.reply("%s plugins already have data .. use -f to force upgrade" % ' .. '.join(alreadygot))
    if errors:
        ievent.reply("errors: ", errors, dot=True)

cmnds.add('plug-upgrade', handle_plugupgrade, 'OPER', options={'-f': ''})
examples.add('plug-upgrade', 'plug-upgrade {<list of plugs>] .. \
upgrade all plugins or a specified plugin', 'plug-upgrade url')
tests.add('plug-upgrade url', 'url')
