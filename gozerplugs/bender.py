# plugs/bender.py
#
#
#

""" uses the random lib """

__copyright__ = 'this file is in the public domain'
__revision__ = '$Id: bender.py 517 2007-02-04 11:17:00Z deck $'

from gozerbot.generic import handle_exception
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
from gozerbot.tests import tests
import re, random

plughelp.add('bender', 'display a bender quote')

benders=["Bite my shiny, metal ass!",
 "Bite my glorious, golden ass!",
 "Bite my shiny, colossal ass!",
 "Bite my splintery, wooden ass!",
 "Lick my frozen, metal ass!",
 "Like most of life's problems, this one can be solved with bending.",
 "Cheese it!",
 "Well, I'm boned.",
 "Hey, sexy mama...wanna kill all humans?",
 "Oh! Your! God!",
 "He's pending for a bending!",
 "This is the worst kind of discrimination - the kind against me!",
 "In case of emergency, my ass can be used as a flotation device.",
 "In order to get busy at maximum efficiency, I need a girl with a big, 400-ton booty.",
 "I'm sick of shaking my booty for these fat jerks!",
 "Bite my red-hot glowing ass!",
 "All I know is, this gold says it was the best mission ever.",
 "Hey, guess what you're all accessories to.",
 "Well, I don't have anything else planned for today. Let's get drunk!",
 "Oh, no room for Bender, huh? Fine! I'll go build my own lunar lander! With blackjack and hookers! In fact, forget the lunar lander and the blackjack! Ah, screw the whole thing.",
 "I found it in the street! Like all the food I cook.",
 "I can't stand idly by while poor people get free food!",
 "Congratulations Fry, you've snagged the perfect girlfriend. Amy's rich, she's probably got other characteristics...",
 "You may need to metaphorically make a deal with the devil. By 'devil' I mean robot devil and by 'metaphorically' I mean get your coat.",
 "Boy, who knew a cooler could also make a handy wang coffin?",
 "Call me old fashioned but I like a dump to be as memorable as it is devastating.",
 "My life, and by extension everyone else's is meaningless.",
 "Do I preach to you while you're lying stoned in the gutter? No.",
 "Everybody's a jerk. You, me, this jerk.",
 "I hate the people that love me and they hate me.",
 "I've personalized each of your meals. Amy, you're cute, so I baked you a pony!",
 "Ahh, computer dating. It's like pimping, but you rarely have to use the phrase, 'upside your head'.",
 "Court's kinda fun when it's not my ass on the line!",
 "Maybe you can interface with my ass! By biting it!",
 "Well, I'll go build my own theme park! With blackjack and hookers! In fact, forget the park!",
 "Compare your lives to mine and then kill yourself!",
 "I would give up my 8 other senses, even smision, for a sense of taste!",
 "Stupid anti-pimping laws!",
 "Blackmail's such an ugly word. I prefer extortion. The x makes it sound cool.",
 "Great is ok, but amazing would be great!",
 "The pie is ready. You guys like swarms of things, right?",
 "Fry cracked corn, and I don't care; Leela cracked corn, I still don't care; Bender cracked corn, and he is great! Take that you stupid corn!",
 "Stay away from our women. You got metal fever, baby, metal fever!",
 "If it ain't black and white, peck, scratch and bite.",
 "Life is hilariously cruel.",
 "Pardon me, brother. Care to donate to the anti-mugging you fund?",
 "I love this planet. I've got wealth, fame, and access to the depths of sleaze that those things bring.",
 "C'mon, it's just like making love. Y'know, left, down, rotate sixty-two degrees, engage rotors...",
 "Oh my God, I'm so excited I wish I could wet my pants.",
 "Argh. The laws of science be a harsh mistress.",
 "In the event of an emergency, my ass can be used as a floatation device.",
 "Hey, I got a busted ass here! I don't see anyone kissing it.",
 "I'm a fraud - a poor, lazy, sexy fraud.",
 "This'll show those filthy bastards who's loveable!"]

def handle_bender(bot, ievent):
    ievent.reply(random.choice(benders))
    
cmnds.add('bender', handle_bender, 'USER')
examples.add('bender', 'show a bender quote', 'bender')
tests.add('bender')
