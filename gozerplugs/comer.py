#!/usr/bin/python
from gozerbot.callbacks import callbacks, jcallbacks
from gozerbot.examples import examples
from gozerbot.commands import cmnds
from gozerbot.plughelp import plughelp

plughelp.add('comer', 'Lunch people tracker')
eat_command="comer" ; goph=" vamos a comer "; whoph=" planean comer ";
addph=" va a comer "; delph=" ya no va a comer " ; clearph=" ha borrado la lista: "
lists={}

def get_list(ievent, nick):
    ievent.reply('Not yet implemented')
    return "none"

def dudes_handler(ievent, name, action, list):
    if list not in lists: ievent.reply("Hey, you're not on any list, and you didn't specify one"); return
    if action == "add": lists[list].add(name); ievent.reply(name + addph + list)
    elif action == "del": lists[list].discard(name); ievent.reply (name + delph + list)
    elif action == "clean": lists[list].clear(); ievent.reply(name + clearph + list)
    elif action == "go": ievent.reply(" ".join(["%s" %k for k in lists[list]]) + goph + list ); lists[list].clear()
    elif action == "who": ievent.reply(" ".join(["%s" %k for k in lists[list]]) + whoph + list )

def handle_eat(bot,ievent):
    try: (action, list) = (ievent.args[0],ievent.args[1])
    except: action = ievent.args; list = get_list(ievent, ievent.nick)

    try:
       if not list:
          if action == "add": ievent.reply("Hey! Where do you eat today?"); return;
       else:
          if list not in lists: lists[list]=set()
    except: pass

    dudes_handler(ievent, ievent.nick, action, list)

cmnds.add(eat_command,handle_eat,'USER')
examples.add(eat_command,"Manages lunch list",'comer add tupper, comer del [list], comer go [list], comer clean [list]')
