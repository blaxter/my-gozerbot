# plugs/search.py
#
#

from gozerbot.generic import handle_exception
from gozerbot.commands import cmnds
from gozerbot.plugins import plugins
from gozerbot.threads.thr import start_new_thread
from gozerbot.plughelp import plughelp
from gozerbot.examples import examples
import Queue

plughelp.add('search', 'search all plugins that provide a search() function')

def handle_search(bot, ievent):
    """ search all plugins that provide a search() function """
    result = {}
    queue = Queue.Queue()
    try:
        what = ievent.args[0]
    except IndexError:
        ievent.missing('<what>')
        return
    threads = []
    for name, plug in plugins.plugs.iteritems():
        try:
            searchfunc = getattr(plug, 'search')
            if searchfunc:
                threadid = start_new_thread(searchfunc, (what, queue))
                threads.append(threadid)
        except AttributeError:
            pass
        except Exception, ex:
            handle_exception()
    for i in threads:
        i.join()
    queue.put(None)
    result = []
    while 1:
        res = queue.get_nowait()
        if not res:
            break
        result.append(res)
    ievent.reply('search results for %s => ' % what, result, dot=True)

cmnds.add('search', handle_search, ['USER', 'CLOUD', 'WEB'])
examples.add('search', 'search all bot data for <item>', 'search gozer')
