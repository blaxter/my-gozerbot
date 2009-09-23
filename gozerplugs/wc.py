# encoding: utf-8
from gozerbot.commands import cmnds
from threading import Semaphore

COMMAND_WC = "wc"
COMMAND_WC_DONE = "wc_done"

class Wc:
    def __init__(self):
        self.sem = Semaphore(1)
        self.user = None
        self.waiting = []

    def used_by(self, who):
        self.user = who
        self.waiting.remove(who)

    def being_used_by(self, who):
        return self.user == who

    def acquire(self, a):
        return self.sem.acquire(a)

    def release(self):
        self.user = None
        self.sem.release()

    def enqueue(self, nick):
        self.waiting.append(nick)

    def is_waiting(self, nick):
        return (nick in self.waiting)

wc = Wc()

def handle_wc_done(bot, ievent):
    if wc.being_used_by(ievent.nick):
        wc.release()
        ievent.reply("Espero que hayas disfrutado de la visita @ "+ ievent.nick)
    else:
        ievent.reply("No estabas en el baño co")

def handle_wc(bot, ievent):
    if wc.being_used_by(ievent.nick):
        ievent.reply("¿No estabas en el baño? @" + ievent.nick)
        return
    elif wc.is_waiting(ievent.nick):
        ievent.reply("Todavía no " + ievent.nick)
        return
    wc.enqueue(ievent.nick)
    if not wc.acquire(False):
        ievent.reply("Está siendo usado, cuando esté libre te aviso chavalote")
        wc.acquire(True)
    wc.used_by(ievent.nick)
    ievent.reply("El baño es todo tuyo @ " + ievent.nick)

cmnds.add(COMMAND_WC, handle_wc, 'ANY')
cmnds.add(COMMAND_WC_DONE, handle_wc_done, 'ANY')
