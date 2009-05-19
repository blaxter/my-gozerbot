# gozerplugs/buzz.py
#
#

__author__ = 'unknown'

from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp

plughelp.add('buzz', 'create a buzz word')

from random import randint

verb = ["implement","utilize","integrate","streamline","optimize",
	"evolve","transform","embrace","enable","orchestrate","leverage",
	"reinvent","aggregate","architect","enhance","incentivize","morph",
	"empower","envisioneer","monetize","harness","facilitate","seize",
	"disintermediate","synergize","strategize","deploy","brand","grow",
	"brand","grow","target","syndicate","synthesize","deliver","mesh",
	"incubate","engage","maximize","benchmark","expedite","reintermediate", 
	"expedite","reintermediate","whiteboard","visualize","repurpose",
	"innovate","scale","unleash","drive","extend","engineer",
	"revolutionize","generate","exploit","transition","e-enable","iterate",
	"cultivate","matrix","productize","redefine","recontextualize"]

adj = ["clicks-and-mortar","value-added","vertical","proactive",
	"robust","revolutionary","scalable","leading-edge","innovative",
	"intuitive","strategic","e-business","mission-critical","sticky",
	"one-to-one","24/7","end-to-end","global","B2B","B2C","granular",
	"frictionless","virtual","viral","dynamic","24/365","best-of-breed",
	"killer","magnetic","bleeding-edge","web-enabled","interactive",
	"dot-com","sexy","back-end","real-time","efficient","front-end",
	"distributed","seamless","extensible","turn-key","world-class",
	"open-source","cross-platform","cross-media","synergistic",
	"bricks-and-clicks","out-of-the-box","enterprise","integrated",
	"impactful","wireless","transparent","next-generation","cutting-edge",
	"user-centric","visionary","customized","ubiquitous","plug-and-play",
	"collaborative","compelling","holistic","rich"]

noun = ["synergies","web-readiness","paradigms","markets","partnerships",
	"infrastructures","platforms", "initiatives","channels","eyeballs",
	"communities","ROI","solutions","e-tailers","e-services","action-items",
	"portals","niches","technologies","content","vortals","supply-chains",
	"convergence","relationships", "architectures","interfaces","e-markets",
	"e-commerce","systems","bandwidth","infomediaries","models","mindshare",
	"deliverables","users","schemas","networks","applications","metrics",
	"e-business","functionalities","experiences","web services",
	"methodologies"]

def rarr(arr):
   return randint(0,len(arr)-1)

def handle_buzz(bot, ievent):
   ievent.reply("%s %s %s" % (verb[rarr(verb)],adj[rarr(adj)],noun[rarr(noun)]))


cmnds.add('buzz', handle_buzz, 'USER')
examples.add('buzz', 'generate buzz', 'buzz')
