# plugs/wisdom.py
#
#

__copyright__ = 'this file is in the public domain'
__thnx__ = 'thnx to snore for this one'

from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
import os, string, random

plughelp.add('wisdom', 'show some wisdom')

excuses = []
matrix = []
motivation = []

def init():
    global excuses
    global matrix
    global motivation
    excuses = excusestxt.splitlines()
    matrix = matrixtxt.splitlines()
    motivation = motivationtxt.splitlines()
    return 1

def handle_matrix(bot, ievent):
    """ get a matrix quote """
    rand = random.randint(0,len(matrix)-1)
    ievent.reply(matrix[rand].strip())

def handle_excuse(bot, ievent):
    """ get an excuse """
    rand = random.randint(0,len(excuses)-1)
    ievent.reply(excuses[rand].strip())

def handle_motivation(bot, ievent):
    """ get despair  """
    rand = random.randint(0,len(motivation)-1)
    ievent.reply(motivation[rand].strip())


cmnds.add('matrix', handle_matrix, 'USER')
examples.add('matrix', 'get a matrix quote', 'matrix')
cmnds.add('excuse', handle_excuse, 'USER')
examples.add('excuse', 'get an excuse', 'excuse')
cmnds.add('motivation', handle_motivation, 'USER')
examples.add('motivation', 'get motivated', 'motivation')

excusestxt = """
clock speed
solar flares
electromagnetic radiation from satellite debris
static from nylon underwear
static from plastic slide rules
global warming
poor power conditioning
static buildup
doppler effect
hardware stress fractures
magnetic interferance from money/credit cards
dry joints on cable plug
we're waiting for [the phone company] to fix that line
sounds like a Windows problem, try calling Microsoft support
temporary routing anomoly
somebody was calculating pi on the server
fat electrons in the lines
excess surge protection
floating point processor overflow
divide-by-zero error
POSIX complience problem
monitor resolution too high
improperly oriented keyboard
network packets travelling uphill (use a carrier pigeon)
Decreasing electron flux
first Saturday after first full moon in Winter
radiosity depletion
CPU radiator broken
It works the way the Wang did, what's the problem
positron router malfunction
cellular telephone interference
techtonic stress
pizeo-electric interference
(l)user error
working as designed
dynamic software linking table corrupted
heavy gravity fluctuation, move computer to floor rapidly
secretary plugged hairdryer into UPS
terrorist activities
not enough memory, go get system upgrade
interrupt configuration error
spaghetti cable cause packet failure
boss forgot system password
bank holiday - system operating credits  not recharged
virus attack, luser responsible
waste water tank overflowed onto computer
Complete Transient Lockout
bad ether in the cables
Bogon emissions
Change in Earth's rotational speed
Cosmic ray particles crashed through the hard disk platter
Smell from unhygenic janitorial staff wrecked the tape heads
Little hamster in running wheel had coronary; waiting for replacement to be Fedexed from Wyoming
Evil dogs hypnotized the night shift
Plumber mistook routing panel for decorative wall fixture
Electricians made popcorn in the power supply
Groundskeepers stole the root password
high pressure system failure
failed trials, system needs redesigned
system has been recalled
not approved by the FCC
need to wrap system in aluminum foil to fix problem
not properly grounded, please bury computer
CPU needs recalibration
system needs to be rebooted
bit bucket overflow
descramble code needed from software company
only available on a need to know basis
knot in cables caused data stream to become twisted and kinked
nesting roaches shorted out the ether cable
The file system is full of it
Satan did it
Daemons did it
You're out of memory
There isn't any problem
Unoptimized hard drive
Typo in the code
Yes, yes, its called a desgin limitation
Look, buddy:  Windows 3.1 IS A General Protection Fault.
That's a great computer you have there; have you considered how it would work as a BSD machine?
Please excuse me, I have to circuit an AC line through my head to get this database working.
Yeah, yo mama dresses you funny and you need a mouse to delete files.
Support staff hung over, send aspirin and come back LATER.
Someone is standing on the ethernet cable, causeing a kink in the cable
Windows 95 undocumented "feature"
Runt packets
Password is too complex to decrypt
Boss' kid fucked up the machine
Electromagnetic energy loss
Budget cuts
Mouse chewed through power cable
Stale file handle (next time use Tupperware(tm)!)
Feature not yet implimented
Internet outage
Pentium FDIV bug
Vendor no longer supports the product
Small animal kamikaze attack on power supplies
The vendor put the bug there.
SIMM crosstalk.
IRQ dropout
Collapsed Backbone
Power company testing new voltage spike (creation) equipment
operators on strike due to broken coffee machine
backup tape overwritten with copy of system manager's favourite CD
UPS interrupted the server's power
The electrician didn't know what the yellow cable was so he yanked the ethernet out.
The keyboard isn't plugged in
The air conditioning water supply pipe ruptured over the machine room
The electricity substation in the car park blew up.
The rolling stones concert down the road caused a brown out
The salesman drove over the CPU board.
The monitor is plugged into the serial port
Root nameservers are out of sync
electro-magnetic pulses from French above ground nuke testing.
your keyboard's space bar is generating spurious keycodes.
the real ttys became pseudo ttys and vice-versa.
the printer thinks its a router.
the router thinks its a printer.
evil hackers from Serbia.
we just switched to FDDI.
halon system went off and killed the operators.
because Bill Gates is a Jehovah's witness and so nothing can work on St. Swithin's day.
user to computer ratio too high.
user to computer ration too low.
we just switched to Sprint.
it has Intel Inside
Sticky bits on disk.
Power Company having EMP problems with their reactor
The ring needs another token
new management
telnet: Unable to connect to remote host: Connection refused
SCSI Chain overterminated
It's not plugged in.
because of network lag due to too many people playing deathmatch
You put the disk in upside down.
Daemons loose in system.
User was distributing pornography on server; system seized by FBI.
BNC (brain not  (user brain not connected)
UBNC (user brain not connected)
LBNC (luser brain not connected)
disks spinning backwards - toggle the hemisphere jumper.
new guy cross-connected phone lines with ac power bus.
had to use hammer to free stuck disk drive heads.
Too few computrons available.
Flat tire on station wagon with tapes.  ("Never underestimate the bandwidth of a station wagon full of tapes hurling down the highway" Andrew S. Tanenbaum) 
Communications satellite used by the military for star wars.
Party-bug in the Aloha protocol.
Insert coin for new game
Dew on the telephone lines.
Arcserve crashed the server again.
Some one needed the powerstrip, so they pulled the switch plug.
My pony-tail hit the on/off switch on the power strip.
Big to little endian conversion error
You can tune a file system, but you can't tune a fish (from most tunefs man pages)
Dumb terminal
Zombie processes haunting the computer
Incorrect time syncronization
Defunct processes
Stubborn processes
non-redundant fan failure 
monitor VLF leakage
bugs in the RAID
no "any" key on keyboard
root rot
Backbone Scoliosis
/pub/lunch
excessive collisions & not enough packet ambulances
le0: no carrier: transceiver cable problem?
broadcast packets on wrong frequency
popper unable to process jumbo kernel
NOTICE: alloc: /dev/null: filesystem full
pseudo-user on a pseudo-terminal
Recursive traversal of loopback mount points
Backbone adjustment
OS swapped to disk
vapors from evaporating sticky-note adhesives
sticktion
short leg on process table
multicasts on broken packets
ether leak
Atilla the Hub
endothermal recalibration
filesystem not big enough for Jumbo Kernel Patch
loop found in loop in redundant loopback
system consumed all the paper for paging
permission denied
Reformatting Page. Wait...
..disk or the processor is on fire.
SCSI's too wide.
Proprietary Information.
Just type 'mv * /dev/null'.
runaway cat on system.
Did you pay the new Support Fee?
We only support a 1200 bps connection.
We only support a 28000 bps connection.
Me no internet, only janitor, me just wax floors.
I'm sorry a pentium won't do, you need an SGI to connect with us.
Post-it Note Sludge leaked into the monitor.
the curls in your keyboard cord are losing electricity.
The monitor needs another box of pixels.
RPC_PMAP_FAILURE
kernel panic: write-only-memory (/dev/wom0) capacity exceeded.
Write-only-memory subsystem too slow for this machine. Contact your local dealer.
Just pick up the phone and give modem connect sounds. "Well you said we should get more lines so we don't have voice lines."
Quantum dynamics are affecting the transistors
Police are examining all internet packets in the search for a narco-net-traficer
We are currently trying a new concept of using a live mouse.  Unfortuantely, one has yet to survive being hooked up to the computer.....please bear with us.
Your mail is being routed through Germany ... and they're censoring us.
Only people with names beginning with 'A' are getting mail this week (a la Microsoft)
We didn't pay the Internet bill and it's been cut off.
Lightning strikes.
Of course it doesn't work. We've performed a software upgrade.
Change your language to Finnish.
Flourescent lights are generating negative ions. If turning them off doesn't work, take them out and put tin foil on the ends.
High nuclear activity in your area.
What office are you in? Oh, that one.  Did you know that your building was built over the universities first nuclear research site? And wow, are'nt you the lucky one, your office is right over where the core is buried!
The MGs ran out of gas.
The UPS doesn't have a battery backup.
Recursivity.  Call back if it happens again.
Someone thought The Big Red Button was a light switch.
The mainframe needs to rest.  It's getting old, you know.
I'm not sure.  Try calling the Internet's head office -- it's in the book.
The lines are all busy (busied out, that is -- why let them in to begin with?).
Jan  9 16:41:27 huber su: 'su root' succeeded for .... on /dev/pts/1
It's those computer people in X {city of world}.  They keep stuffing things up.
A star wars satellite accidently blew up the WAN.
Fatal error right in front of screen
That function is not currently supported, but Bill Gates assures us it will be featured in the next upgrade.
wrong polarity of neutron flow
Lusers learning curve appears to be fractal
We had to turn off that service to comply with the CDA Bill.
Ionisation from the air-conditioning
TCP/IP UDP alarm threshold is set too low.
Someone is broadcasting pigmy packets and the router dosn't know how to deal with them.
The new frame relay network hasn't bedded down the software loop transmitter yet. 
Fanout dropping voltage too much, try cutting some of those little traces
Plate voltage too low on demodulator tube
You did wha... oh _dear_....
CPU needs bearings repacked
Too many little pins on CPU confusing it, bend back and forth until 10-20% are neatly removed. Do _not_ leave metal bits visible!
_Rosin_ core solder? But...
Software uses US measurements, but the OS is in metric...
The computer fletely, mouse and all.
Your cat tried to eat the mouse.
The Borg tried to assimilate your system. Resistance is futile.
It must have been the lightning storm we had (yesterdy) (last week) (last month)
Due to Federal Budget problems we have been forced to cut back on the number of users able to access the system at one time. (namely none allowed....)
Too much radiation coming from the soil.
Unfortunately we have run out of bits/bytes/whatever. Don't worry, the next supply will be coming next week.
Program load too heavy for processor to lift.
Processes running slowly due to weak power supply
Our ISP is having {switching,routing,SMDS,frame relay} problems
We've run out of licenses
Interference from lunar radiation
Standing room only on the bus.
You need to install an RTFM interface.
That would be because the software doesn't work.
That's easy to fix, but I can't be bothered.
Someone's tie is caught in the printer, and if anything else gets printed, he'll be in it too.
We're upgrading /dev/null
The Usenet news is out of date
Our POP server was kidnapped by a weasel.
It's stuck in the Web.
Your modem doesn't speak English.
The mouse escaped.
All of the packets are empty.
The UPS is on strike.
Neutrino overload on the nameserver
Melting hard drives
Someone has messed up the kernel pointers
The kernel license has expired
Netscape has crashed
The cord jumped over and hit the power switch.
It was OK before you touched it.
Bit rot
U.S. Postal Service
Your Flux Capacitor has gone bad.
The Dilithium Cyrstals need to be rotated.
The static electricity routing is acting up...
Traceroute says that there is a routing problem in the backbone.  It's not our problem.
The co-locator cannot verify the frame-relay gateway to the ISDN server.
High altitude condensation from U.S.A.F prototype aircraft has contaminated the primary subnet mask. Turn off your computer for 9 days to avoid damaging it.
Lawn mower blade in your fan need sharpening
Electrons on a bender
Telecommunications is upgrading. 
Telecommunications is downgrading.
Telecommunications is downshifting.
Hard drive sleeping. Let it wake up on it's own...
Interference between the keyboard and the chair.
The CPU has shifted, and become decentralized.
Due to the CDA, we no longer have a root account.
We ran out of dial tone and we're and waiting for the phone company to deliver another bottle.
You must've hit the wrong anykey.
PCMCIA slave driver
The Token fell out of the ring. Call us when you find it.
The hardware bus needs a new token.
Too many interrupts
Not enough interrupts
The data on your hard drive is out of balance.
Digital Manipulator exceeding velocity parameters
appears to be a Slow/Narrow SCSI-0 Interface problem
microelectronic Riemannian curved-space fault in write-only file system
fractal radiation jamming the backbone
routing problems on the neural net
IRQ-problems with the Un-Interruptable-Power-Supply
CPU-angle has to be adjusted because of vibrations coming from the nearby road
emissions from GSM-phones
CD-ROM server needs recalibration
firewall needs cooling
asynchronous inode failure
transient bus protocol violation
incompatible bit-registration operators
your process is not ISO 9000 compliant
You need to upgrade your VESA local bus to a MasterCard local bus.
The recent proliferation of Nuclear Testing
Elves on strike. (Why do they call EMAG Elf Magic)
Internet exceeded Luser level, please wait until a luser logs off before attempting to log back on.
Your EMAIL is now being delivered by the USPS.
Your computer hasn't been returning all the bits it gets from the Internet.
You've been infected by the Telescoping Hubble virus.
Scheduled global CPU outage
Your Pentium has a heating problem - try cooling it with ice cold water.(Do not turn of your computer, you do not want to cool down the Pentium Chip while he isn't working, do you?)
Your processor has processed too many intructions.  Turn it off emideately, do not type any commands!!
Your packets were eaten by the terminator
Your processor does not develop enough heat.
We need a licensed electrician to replace the light bulbs in the computer room.
The POP server is out of Coke
Fiber optics caused gas main leak
Server depressed, needs Prozak
quatnum decoherence
those damn racoons!
suboptimal routing experience
A plumber is needed, the network drain is clogged
50% of the manual is in .pdf readme files
the AA battery in the wallclock sends magnetic interference
the xy axis in the trackball is coordinated with the summer soltice
the butane lighter causes the pincushioning
old inkjet cartridges emanate barium-based fumes
manager in the cable duct
We'll fix that in the next (upgrade, update, patch release, service pack).
HTTPD Error 666 : BOFH was here
HTTPD Error 4004 : very old Intel cpu - insufficient processing power
The ATM board has run out of 10 pound notes.  We are having a whip round to refill it, care to contribute ?
Network failure -  call NBC
Having to manually track the satellite.
Your/our computer(s) had suffered a memory leak, and we are waiting for them to be topped up.
The rubber band broke
We're on Token Ring, and it looks like the token got loose.
Stray Alpha Particles from memory packaging caused Hard Memory Error on Server.
paradigm shift...without a clutch
PEBKAC (Problem Exists Between Keyboard And Chair)
The cables are not the same length.
Second-sytem effect.
Chewing gum on /dev/sd3c
Boredom in the Kernel.
the daemons! the daemons! the terrible daemons!
I'd love to help you -- it's just that the Boss won't let me near the computer. 
struck by the Good Times virus
YOU HAVE AN I/O ERROR -> Incompetent Operator error
Your parity check is overdrawn and you're out of cache.
Communist revolutionaries taking over the server room and demanding all the computers in the building or they shoot the sysadmin. Poor misguided fools.
Plasma conduit breach
Out of cards on drive D:
Sand fleas eating the Internet cables
parallel processors running perpendicular today
ATM cell has no roaming feature turned on, notebooks can't connect
Webmasters kidnapped by evil cult.
Failure to adjust for daylight savings time.
Virus transmitted from computer to sysadmins.
Virus due to computers having unsafe sex.
Incorrectly configured static routes on the corerouters.
Forced to support NT servers; sysadmins quit.
Suspicious pointer corrupted virtual machine
Its the InterNIC's fault.
Root name servers corrupted.
Budget cuts forced us to sell all the power cords for the servers.
Someone hooked the twisted pair wires into the answering machine.
Operators killed by year 2000 bug bite.
We've picked COBOL as the language of choice.
Operators killed when huge stack of backup tapes fell over.
Robotic tape changer mistook operator's tie for a backup tape.
Someone was smoking in the computer room and set off the halon systems.
Your processor has taken a ride to Heaven's Gate on the UFO behind Hale-Bopp's comet.
t's an ID-10-T error
Dyslexics retyping hosts file on servers
The Internet is being scanned for viruses.
Your computer's union contract is set to expire at midnight.
Bad user karma.
/dev/clue was linked to /dev/null
Increased sunspot activity.
We already sent around a notice about that.
It's union rules. There's nothing we can do about it. Sorry.
Interferance from the Van Allen Belt.
Jupiter is aligned with Mars.
Redundant ACLs. 
Mail server hit by UniSpammer.
T-1's congested due to porn traffic to the news server.
Data for intranet got routed through the extranet and landed on the internet.
We are a 100% Microsoft Shop.
We are Microsoft.  What you are experiencing is not a problem; it is an undocumented feature.
Sales staff sold a product we don't offer.
Secretary sent chain letter to all 5000 employees.
Sysadmin didn't hear pager go off due to loud music from bar-room speakers.
Sysadmin accidentally destroyed pager with a large hammer.
Sysadmins unavailable because they are in a meeting talking about why they are unavailable so much.
Bad cafeteria food landed all the sysadmins in the hospital.
Route flapping at the NAP.
Computers under water due to SYN flooding.
The vulcan-death-grip ping has been applied.
Electrical conduits in machine room are melting.
Traffic jam on the Information Superhighway.
Radial Telemetry Infiltration
Cow-tippers tipped a cow onto the server.
tachyon emissions overloading the system
Maintence window broken
We're out of slots on the server
Computer room being moved.  Our systems are down for the weekend.
Sysadmins busy fighting SPAM.
Repeated reboots of the system failed to solve problem
Feature was not beta tested
Domain controler not responding
Someone else stole your IP address, call the Internet detectives!
It's not RFC-822 compliant.
operation failed because: there is no message for this error (#1014)
stop bit received
internet is needed to catch the etherbunny
network down, IP packets delivered via UPS
Firmware update in the coffee machine
Temporal anomaly
Mouse has out-of-cheese-error
Borg implants are failing
Borg nanites have infested the server
error: one bad user found in front of screen
Please state the nature of the technical emergency
Internet shut down due to maintainance
Daemon escaped from pentagram
crop circles in the corn shell
sticky bit has come loose
Hot Java has gone cold
Cache miss - please take better aim next time
Hash table has woodworm
Trojan horse ran out of hay
Zombie processess detected, machine is haunted.
overflow error in /dev/null
Browser's cookie is corrupted -- someone's been nibbling on it.
Mailer-daemon is busy burning your message in hell.
According to Microsoft, it's by design
vi needs to be upgraded to vii
greenpeace free'd the mallocs
Terorists crashed an airplane into the server room, have to remove /bin/laden. (rm -rf /bin/laden)
"""

matrixtxt = """
<morpheus> If real is what you can feel, smell, taste and see, then 'real' is simply electrical signals interpreted by your brain
<morpheus> What are you waiting for? You're faster than this. Don't think you are, know you are. Come on! Stop trying to hit me and hit me!
<Morpheus> Unfortunately, no one can be told what the Matrix is. You have to see it for yourself.
<morpheus> What you know you can't explain, but you feel it. You've felt it your entire life, that there's something wrong with the world. You don't know what it is, but it's there, like a splinter in your mind, driving you mad.
<morpheus> You have the look of a man who accepts what he sees because he is expecting to wake up. Ironically, that's not far from the truth.
<morpheus> I'm trying to free your mind, Neo. But I can only show you the door. You're the one that has to walk through it.
<neo> Why do my eyes hurt? <morpheus> You've never used them before.
<morpheus> There is a difference between knowing the path and walking the path.
<neo> What are you trying to tell me? That I can dodge bullets? <morpheus> No, Neo. I'm trying to tell you that when you're ready, you won't have to.
<morpheus> The Matrix is the world that has been pulled over your eyes to blind you from the truth.
<morpheus> You've been living in a dream world, Neo.
<morpheus> I imagine that right now you're feeling a bit like Alice, tumbling down the rabbit hole.
<morpheus> What is "real"? How do you define "real"?
<morpheus> Welcome to the desert of the real.
<morpheus> You have to let it all go, Neo. Fear, doubt, and disbelief. Free your mind.
<neo> Am I dead? <morpheus> Far from it.
<morpheus> You are the One, Neo. You see, you may have spent the last few years looking for me, but I have spent my entire life looking for you.
<morpheus> This is your last chance. After this, there is no turning back. You take the blue pill - the story ends, you wake up in your bed and believe whatever you want to believe. You take the red pill - you stay in Wonderland and I show you how deep the rabbit-hole goes.
<morpheus> I've seen an agent punched through a concrete wall. Men have emptied entire clips at them and hit nothing but air, yet their strength and their speed are still based in a world that is built on rules. Because of that, they will never be as strong or as fast as you can be. 
<rhineheart> You have a problem with authority, Mr. Anderson.
<tank> Hey Mikey I think he likes it.
<morpheus> It IS our destiny
<agent smith> Never send a human to do a machine's job.
<morpheus> Focus, trinity
<agent smith> Do you hear that, Mr. Anderson? That is the sound of inevitability
<spoon boy> There is no spoon. 
<tank> So what do you need? Besides a miracle <neo> Guns. Lots of guns.
<trinity> Neo... nobody has ever done this before. <neo> I know. That's why it's going to work.
<neo> I know kung fu
<neo> Okey dokey.. free my mind. Right, no problem, free my mind, free my mind, no problem, right...
<cypher> Good shit, huh? It's good for two things: degreasing engines and killing brain cells.
<cypher> All I see now is blonde, brunette, redhead.
"""

motivationtxt = """
Achievement: You can do anything you set your mind to when you have vision, determination, and an endless supply of expendable labor. 
Adversity: That which does not kill me postpones the inevitable. 
Agony: Not all pain is gain. 
Ambition: The journey of a thousand miles sometimes ends very, very badly.
Apathy: If we don't take care of the customer,maybe they'll stop bugging us.
Arrogance: The best leaders inspire by example. When that's not an option, brute intimidation works pretty well, too.
Beauty: If you're attractive enough on the outside, people will forgive you for being irritating to the core.
Bitterness: Never be afraid to share your dreams with the world, because there's nothing the world loves more than the taste of really sweet dreams.
Blame: The secret to success is knowing who to blame for your failures.
Burnout: Attitudes are contagious. Mine might kill you. 
Change: It's a short trip from riding the waves of change to being torn apart by the jaws of defeat. 
Change (winds): When the winds of change blow hard enough, the most trivial of things can become deadly projectiles.
Cluelessness: There are no stupid questions, but there are a LOT of inquisitive idiots.
Compromise: Let's agree to respect each others views, no matter how wrong yours may be.
Conformity: When people are free to do as they please, they usually imitate each other.
Consulting: If you're not a part of the solution,there's good money to be made in prolonging the problem. 
Dare to Slack: When birds fly in the right formation, they need only exert half the effort. Even in nature, teamwork results in collective laziness.
Defeat: For every winner, there are dozens of losers. Odds are you're one of them.
Delusions: There is no greater joy than soaring high on the wings of your dreams, except maybe the joy of watching a dreamer who has nowhere to land but in the ocean of reality. 
Demotivation: Sometimes the best solution to morale problems is just to fire all of the unhappy people. 
Despair: It's always darkest just before it goes pitch black. 
Destiny: You were meant for me. Perhaps as a punishment.
Discovery: A company that will go to the ends of the Earth for its people will find it can hire them for about 10% of the cost of Americans.
Disloyalty: There comes a time when every team must learn to make individual sacrifices.
Disservice: It takes months to find a customer, but only seconds to lose one... the good news is that we should run out of them in no time.
Do it Later: The early worm is for the birds.
Doubt: In the battle between you and the world, bet on the world.
Dreams: Dreams are like rainbows. Only idiots chase them. 
Dysfunction: The only consistent feature in all of your dissatisfying relationships is you.
Effort: Hard work never killed anybody, but it is illegal in some places. 
Elitism: It's lonely at the top, but it's comforting to look down upon everyone at the bottom.
Failure: When your best just isn't good enough. 
Fear: Until you have the courage to lose sight of the shore, you will not know the terror of being forever lost at sea 
Flattery: If you want to get to the top, prepare to kiss a lot of the bottom.
Futility: You'll always miss 100% of the shots you don't take, and, statistically speaking, 99% of the shots you do. 
Get To Work: You aren't being paid to believe in the power of your dreams. 
Goals: It's best to avoid standing directly between a competitive jerk and his goals. 
Hazards: There is an island of opportunity in the middle of every difficulty.  Miss that, though, and you're pretty much doomed. 
Humiliation: The harder you try, the dumber you look. 
Idiocy: Never underestimate the power of stupid people in large groups. 
Ignorance: It's amazing how much easier it is for a team to work together when no one has any idea where they're going. 
Incompetence: When you earnestly believe you can compensate for a lack of skill by doubling your efforts, there's no end to what you can't do. 
Indifference: It takes 43 muscles to frown and 17 to smile, but it doesn't take any to just sit there with a dumb look on your face.
Individuality: Always remember that you are unique. Just like everybody else. 
Ineptitude: If you can't learn to do something well, learn to enjoy doing it poorly.
Insanity: It's difficult to comprehend how insane some people can be. Especially when you're insane. 
Inspiration: Genius is 1 percent inspiration and 99% perspiration, which is why engineers sometimes smell really bad. 
Intimidation: No one can make you feel inferior without your consent, but you'd be a fool to withhold that from your superiors.
Irresponsibility: No single raindrop believes it is to blame for the flood.
Laziness: Success is a journey, not a destination. So stop running. 
Leaders: Leaders are like eagles. We don't have either of them here. 
Limitations: Until you spread your wings, you'll have no idea how far you can walk.
Loneliness: If you find yourself struggling with loneliness, you're not alone. And yet you are alone. So very alone. 
Losing: If at first you don't succeed, failure may be your style.
Madness: Madness does not always howl. Sometimes, it is the quiet voice at the end of the day saying, "Hey, is there room in your head for one more?"
Mediocrity: It takes a lot less time and most people won't notice the difference until it's too late. 
Meetings: None of us is as dumb as all of us. 
Misfortune: While good fortune often eludes you, this kind never misses. 
Mistakes: It could be that the purpose of your life is only to serve as a warning to others.
Motivation: If a pretty poster and a cute saying are all it takes to motivate you, you probably have a very easy job. The kind robots will be doing soon. 
Nepotism: We promote family values here - almost as often as we promote family members. 
Overconfidence: Before you attempt to beat the odds, be sure you could survive the odds beating you. 
Pessimism: Every dark cloud has a silver lining, but lightning kills hundreds of people each year who are trying to find it. 
Persistence: It's over, man. Let her go.
Planning: Much work remains to be done before we can announce our total failure to make any progress. 
Potential: Not everyone gets to be an astronaut when they grow up.
Power: Power corrupts. Absolute power corrupts absolutely. But it rocks absolutely, too.
Pressure: It can turn a lump of coal into a flawless diamond, or an average person into a perfect basketcase.
Pretension: The downside of being better than everyone else is that people tend to assume you're pretentious. 
Problems: No matter how great and destructive your problems may seem now, remember, you've probably only seen the tip of them 
Procrastination: Hard work often pays off after time, but laziness always pays off now. 
Quality: The race for quality has no finish line- so technically, it's more like a death march. 
Regret: It hurts to admit when you make mistakes - but when they're big enough, the pain only lasts a second 
Retirement: Because you've given so much of yourself to the Company that you don't have anything left we can use. 
Risks: If you never try anything new, you'll miss out on many of life's great disappointments.
Sacrifice: Your role may be thankless, but if you're willing to give it your all, you just might bring success to those who outlast you.
Sacrifice (Temple): All we ask here is that you give us your heart. 
Strife: As long as we have each other, we'll never run out of problems. 
Stupidity: Quitters never win, winners never quit, but those who never win AND never quit are idiots.
Success: Some people dream of success, while other people live to crush those dreams. 
Teamwork: A few harmless flakes working together can unleash an avalanche of destruction.
Trouble: Luck can't last a lifetime unless you die young. 
Underachievement: The tallest blade of grass is the first to be cut by the lawnmower. 
Wishes: When you wish upon a falling star, your dreams can come true. Unless it's really a meteorite hurtling to the Earth which will destroy all life. Then you're pretty much hosed no matter what you wish for. Unless it's death by meteor. 
Worth: Just because you're necessary doesn't mean you're important.
"""
