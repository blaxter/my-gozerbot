from gozerbot.callbacks import callbacks
import re
def marinero_precond(bot, ievent):
    """ remind precondition """
    return re.match("^ar{3,}$", ievent.txt)

def marinero_response(bot, ievent):
    ievent.reply('marinero')

callbacks.add('PRIVMSG', marinero_response, marinero_precond)
