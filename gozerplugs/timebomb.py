# gozerplugs/timebomb.py
#
# Gozerbot Timebomb plugin by Clone 2009 
# Idea not so loosely based on jotham.read@gmail.com's eggdrop timebomb 

""" do the timebomb dance. """

__copyright__ = 'BSD'
__author__ = 'clone at magtar.org'

from gozerbot.generic import getwho
from gozerbot.commands import cmnds
from gozerbot.plughelp import plughelp
from gozerbot.persist.persist import PlugPersist
from gozerbot.aliases import aliasset

from time import sleep, time
from random import randint, shuffle

plughelp.add('timebomb', 'blow your buddies to smithereens !timebomb <victim>')
plughelp.add('cut', 'try to defuse a bomb placed with !timebomb by cutting a wire i.e. !cut blue')

# define plugpersist outside localscope, you only want to initiate it once.
bomb = PlugPersist('bomb')
bomb.data = []

def timebomb(bot, ievent):
    # check if we have ops
    if ievent.channel not in bot.state['opchan']:
        bot.action(ievent.channel, "bends over and farts in %s's general direction." % ievent.nick)
        return
    # check if we are already running a bomb
    if bomb.data:
        bot.action(ievent.channel ,"points at the bulge in %s's pants." % bomb.data[0])
        return
    try:
        userhost = getwho(bot, ievent.args[0])
    except IndexError:
        ievent.reply('timebomb requires victim, see !help timebomb.')
        return
    # check if the victim userhost exists on this channel
    if not userhost:
         ievent.reply('no %s here.' % ievent.args[0])
         return
    else:
        user = ievent.args[0]
    # if bot gets targeted, switch target to caller
    if ievent.args[0].lower() == bot.nick.lower():
         userhost = ievent.ruserhost 
         user = ievent.nick
    # define wires 
    wires = ['blue','black','red','green','purple','white','silver'];
    # determine number of wires and pick random colors
    shuffle(wires)
    mywires = wires[0:randint(2,len(wires)-1)]
    counter = 18 + 2 * len(mywires) + randint(1,12)
    # determine time to mark instance
    instancetime = time()
    # plant bomb: (name to kick, which wires to choose from, which wire disarms, userhost)
    bomb.data = [user, mywires, mywires[randint(0,len(mywires)-1)], userhost, instancetime]
    ievent.reply('%s places a bomb in %s\'s pants, the timer reads %s seconds. You see the wires :%s' % (ievent.nick, user, counter, str(mywires)))
    # wait for timer to expire
    sleep(counter)
    
    # check if persist data still exists (no cut event) and kick if so.
    if bomb.data:
        # data from different instance, dont cut
        if not bomb.data[-1] == instancetime:
           return
        else: 
            #kick victim
            bot.sendraw('KICK %s %s :%s' % (ievent.channel, bomb.data[0], 'B000000M!'))
            #ievent.reply('user: %s, userhost: %s' % (bomb.data[0], bomb.data[3]))
            bomb.data = []

def cut(bot, ievent):
    # check if there is a timebomb running
    if bomb.data:
        # right userhost?
        if bomb.data[3] == ievent.ruserhost:
            # right wire?
            if ievent.args[0] == bomb.data[2]:
                 bomb.data=[]
                 ievent.reply('%s has defused the bomb.' % ievent.nick)
            else:
                bot.sendraw('KICK %s %s :%s' % (ievent.channel, bomb.data[0], 'snip...B000000M!'))
                bomb.data=[]
            
cmnds.add('timebomb', timebomb, 'USER', threaded=True)
aliasset('tb', 'timebomb')
cmnds.add('cut', cut, 'USER', threaded=True)
