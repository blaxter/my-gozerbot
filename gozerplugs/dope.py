from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
import os, string, random

plughelp.add('dope', 'for all the junkies out there')

joint = '''
purple haze
white widow
silver haze
mango haze
krystal
mossad
mexican haze
northern lights
master kush
california orange bud
b-52
binnenkweek mix
skunk
jamaican
jack herrer
tafrolt
pakistaan
primero
red libanon
hija
super hija
afghaan
zwarte afghaan
twizla
malana cream
caramello balls
nepal
maroc
super maroc
charras malana
royal cream
'''.strip().splitlines()

joint_action = '''
rolls a nice %s
passes the %s
gives a large %s joint
puts some %s in the took
fixes a djonko with %s
rolls a blunt with %s
stuffs a waterpipe with %s
smokes %s and gets really high
passes the %s to tashiro
builds a tulp with %s
bakes a %s cake
pulls a %s tea
'''.strip().splitlines()


def handle_joint(bot, ievent):
    """ get a joint  """
    what = random.choice(joint_action) % random.choice(joint)
    bot.action(ievent.channel, what)

cmnds.add('joint', handle_joint, 'USER')
examples.add('joint', 'get a joint', 'joint')

