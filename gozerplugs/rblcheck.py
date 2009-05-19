# Port from r3boot's rblcheck, with added threading support
# (c) Wijnand 'tehmaze' Modderman - http://tehmaze.com
# BSD License
# (c) Lex 'r3boot' van Roon - http://r3blog.nl

rbls = {}
rbls["wl"] = {}
rbls["bl"] = {}

rbls["wl"]["bondedsender"] = [
    "query.bondedsender.org",
    "http://www.bondedsender.org/"
]
rbls["wl"]["cml.anti-spam.org.cn"] = [
    "cml.anti-spam.org.cn",
    "http://anti-spam.org.cn/services/cml.php"
]
rbls["wl"]["dnswl"] = [
    "list.dnswl.org",
    "http://www.dnswl.org/"
]
rbls["wl"]["exemptions.ahbl"] = [
    "exemptions.ahbl.org",
    "http://www.ahbl.org/"
]
rbls["wl"]["iadb"] = [
    "iadb.isipp.com",
    "http://www.isipp.com/iadb.php"
]
rbls["wl"]["iadb2"] = [
    "iadb2.isipp.com",
    "http://www.isipp.com/iadb.php"
]
rbls["wl"]["iddb"] = [
    "iddb.isipp.com",
    "http://www.isipp.com/iadb.php"
]
rbls["wl"]["isoc"] = [
    "dnswl.isoc.bg",
    "http://dnsbl.isoc.bg/"
]
rbls["wl"]["isp.dns.nzl.net"] = [
    "isp.dns.nzl.net",
    "http://www.nzl.net/"
]
rbls["wl"]["nlwhitelist"] = [
    "nlwhitelist.dnsbl.bit.nl",
    "http://virbl.bit.nl/"
]
rbls["wl"]["spamblocked"] = [
    "whitelist.spamblocked.com",
    "http://www.spamblocked.com/"
]
rbls["wl"]["spf.trusted-forwarder.org"] = [
    "spf.trusted-forwarder.org",
    "http://www.trusted-forwarder.org/"
]
rbls["wl"]["whitelist.sci.kun.nl"] = [
    "whitelist.sci.kun.nl",
    "http://whitelist.sci.kun.nl"
]
rbls["bl"]["access.redhawk.org"] = [
    "access.redhawk.org",
    "http://access.redhawk.org"
]
rbls["bl"]["assholes.madscience.nl"] = [
    "assholes.madscience.nl",
    "http://assholes.madscience.nl"
]
rbls["bl"]["badconf.rhsbl.sorbs.net"] = [
    "badconf.rhsbl.sorbs.net",
    "http://www.dnsbl.nl.sorbs.net/"
]
rbls["bl"]["bl.csma.biz"] = [
    "bl.csma.biz",
    "http://bl.csma.biz/"
]
rbls["bl"]["bl.deadbeef.com"] = [
    "bl.deadbeef.com",
    "http://spam.deadbeef.com/bl/"
]
rbls["bl"]["bl.spamcannibal.org"] = [
    "bl.spamcannibal.org",
    "http://spamcannibal.org/"
]
rbls["bl"]["bl.starloop.com"] = [
    "bl.starloop.com",
    "http://bl.starloop.com"
]
rbls["bl"]["bl.technovision.dk"] = [
    "bl.technovision.dk",
    "http://bl.technovision.dk"
]
rbls["bl"]["blackholes.five-ten-sg.com"] = [
    "blackholes.five-ten-sg.com",
    "http://www.five-ten-sg.com/blackhole.php"
]
rbls["bl"]["blackholes.intersil.net"] = [
    "blackholes.intersil.net",
    "http://blackholes.intersil.net"
]
rbls["bl"]["blackholes.mail-abuse.org"] = [
    "blackholes.mail-abuse.org",
    "http://www.mail-abuse.org/rss/"
]
rbls["bl"]["blackholes.sandes.dk"] = [
    "blackholes.sandes.dk",
    "http://blackholes.sandes.dk"
]
rbls["bl"]["blackholes.uceb.org"] = [
    "blackholes.uceb.org",
    "http://www.uceb.org"
]
rbls["bl"]["blacklist.sci.kun.nl"] = [
    "blacklist.sci.kun.nl",
    "http://blacklist.sci.kun.nl"
]
rbls["bl"]["blacklist.spambag.org"] = [
    "blacklist.spambag.org",
    "http://blacklist.spambag.org"
]
rbls["bl"]["block.dnsbl.sorbs.net"] = [
    "block.dnsbl.sorbs.net",
    "http://www.dnsbl.nl.sorbs.net/"
]
rbls["bl"]["blocked.hilli.dk"] = [
    "blocked.hilli.dk",
    "http://blocked.hilli.dk"
]
rbls["bl"]["bogons.dnsiplists.completewhois.com"] = [
    "bogons.dnsiplists.completewhois.com",
    "http://bogons.dnsiplists.completewhois.com"
]
rbls["bl"]["cart00ney.surriel.com"] = [
    "cart00ney.surriel.com",
    "http://cart00ney.surriel.com"
]
rbls["bl"]["cbl.abuseat.org"] = [
    "cbl.abuseat.org",
    "http://cbl.abuseat.org"
]
rbls["bl"]["dev.null.dk"] = [
    "dev.null.dk",
    "http://dev.null.dk/"
]
rbls["bl"]["dialup.blacklist.jippg.org"] = [
    "dialup.blacklist.jippg.org",
    "http://dialup.blacklist.jippg.org"
]
rbls["bl"]["dialups.mail-abuse.org"] = [
    "dialups.mail-abuse.org",
    "http://www.mail-abuse.org/dul/"
]
rbls["bl"]["dialups.visi.com"] = [
    "dialups.visi.com",
    "http://dialups.visi.com"
]
rbls["bl"]["dnsbl-1.uceprotect.net"] = [
    "dnsbl-1.uceprotect.net",
    "http://www.uceprotect.net/en/"
]
rbls["bl"]["dnsbl-2.uceprotect.net"] = [
    "dnsbl-2.uceprotect.net",
    "http://www.uceprotect.net/en/"
]
rbls["bl"]["dnsbl-3.uceprotect.net"] = [
    "dnsbl-3.uceprotect.net",
    "http://www.uceprotect.net/en/"
]
rbls["bl"]["dnsbl.ahbl.org"] = [
    "dnsbl.ahbl.org",
    "http://www.ahbl.org/"
]
rbls["bl"]["dnsbl.antispam.or.id"] = [
    "dnsbl.antispam.or.id",
    "http://dnsbl.antispam.or.id"
]
rbls["bl"]["dnsbl.cyberlogic.net"] = [
    "dnsbl.cyberlogic.net",
    "http://dnsbl.cyberlogic.net"
]
rbls["bl"]["dnsbl.jammconsulting.com"] = [
    "dnsbl.jammconsulting.com",
    "http://www.jammconsulting.com/policies/dnsbl.shtml"
]
rbls["bl"]["dnsbl.kempt.net"] = [
    "dnsbl.kempt.net",
    "http://dnsbl.kempt.net"
]
rbls["bl"]["dnsbl.njabl.org"] = [
    "dnsbl.njabl.org",
    "http://dnsbl.njabl.org"
]
rbls["bl"]["dnsbl.sorbs.net"] = [
    "dnsbl.sorbs.net",
    "http://www.dnsbl.nl.sorbs.net/"
]
rbls["bl"]["dsbl.dnsbl.net.au"] = [
    "dsbl.dnsbl.net.au",
    "http://dsbl.dnsbl.net.au"
]
rbls["bl"]["duinv.aupads.org"] = [
    "duinv.aupads.org",
    "http://duinv.aupads.org"
]
rbls["bl"]["dul.dnsbl.sorbs.net"] = [
    "dul.dnsbl.sorbs.net",
    "http://www.dnsbl.nl.sorbs.net/"
]
rbls["bl"]["dul.maps.vix.com"] = [
    "dul.maps.vix.com",
    "http://dul.maps.vix.com/"
]
rbls["bl"]["dul.orca.bc.ca"] = [
    "dul.orca.bc.ca",
    "http://dul.orca.bc.ca/"
]
rbls["bl"]["dul.ru"] = [
    "dul.ru",
    "http://dul.ru"
]
rbls["bl"]["dun.dnsrbl.net"] = [
    "dun.dnsrbl.net",
    "http://dun.dnsrbl.net"
]
rbls["bl"]["dynablock.njabl.org"] = [
    "dynablock.njabl.org",
    "http://dynablock.njabl.org"
]
rbls["bl"]["fl.chickenboner.biz"] = [
    "fl.chickenboner.biz",
    "http://fl.chickenboner.biz"
]
rbls["bl"]["forbidden.icm.edu.pl"] = [
    "forbidden.icm.edu.pl",
    "http://forbidden.icm.edu.pl"
]
rbls["bl"]["hijacked.dnsiplists.completewhois.com"] = [
    "hijacked.dnsiplists.completewhois.com",
    "http://hijacked.dnsiplists.completewhois.com"
]
rbls["bl"]["hil.habeas.com"] = [
    "hil.habeas.com",
    "http://hil.habeas.com"
]
rbls["bl"]["http.dnsbl.sorbs.net"] = [
    "http.dnsbl.sorbs.net",
    "http://www.dnsbl.nl.sorbs.net/"
]
rbls["bl"]["images-msrbls"] = [
    "images.rbl.msrbl.net",
    "http://www.msrbl.com/"
]
rbls["bl"]["intruders.docs.uu.se"] = [
    "intruders.docs.uu.se",
    "http://intruders.docs.uu.se"
]
rbls["bl"]["korea.services.net"] = [
    "korea.services.net",
    "http://korea.services.net"
]
rbls["bl"]["l1.spews.dnsbl.sorbs.net"] = [
    "l1.spews.dnsbl.sorbs.net",
    "http://l1.spews.dnsbl.sorbs.net"
]
rbls["bl"]["l2.spews.dnsbl.sorbs.net"] = [
    "l2.spews.dnsbl.sorbs.net",
    "http://l2.spews.dnsbl.sorbs.net"
]
rbls["bl"]["mail-abuse.blacklist.jippg.org"] = [
    "mail-abuse.blacklist.jippg.org",
    "http://mail-abuse.blacklist.jippg.org"
]
rbls["bl"]["map.spam-rbl.com"] = [
    "map.spam-rbl.com",
    "http://map.spam-rbl.com"
]
rbls["bl"]["misc.dnsbl.sorbs.net"] = [
    "misc.dnsbl.sorbs.net",
    "http://www.dnsbl.nl.sorbs.net/"
]
rbls["bl"]["msgid.bl.gweep.ca"] = [
    "msgid.bl.gweep.ca",
    "http://msgid.bl.gweep.ca"
]
rbls["bl"]["msrbl"] = [
    "combined.rbl.msrbl.net",
    "http://www.msrbl.com/"
]
rbls["bl"]["no-more-funn.moensted.dk"] = [
    "no-more-funn.moensted.dk",
    "http://moensted.dk/spam/no-more-funn/"
]
rbls["bl"]["nomail.rhsbl.sorbs.net"] = [
    "nomail.rhsbl.sorbs.net",
    "http://www.dnsbl.nl.sorbs.net/"
]
rbls["bl"]["ohps.dnsbl.net.au"] = [
    "ohps.dnsbl.net.au",
    "http://ohps.dnsbl.net.au"
]
rbls["bl"]["okrelays.nthelp.com"] = [
    "okrelays.nthelp.com",
    "http://okrelays.nthelp.com"
]
rbls["bl"]["omrs.dnsbl.net.au"] = [
    "omrs.dnsbl.net.au",
    "http://omrs.dnsbl.net.au"
]
rbls["bl"]["orid.dnsbl.net.au"] = [
    "orid.dnsbl.net.au",
    "http://orid.dnsbl.net.au"
]
rbls["bl"]["orvedb.aupads.org"] = [
    "orvedb.aupads.org",
    "http://orvedb.aupads.org"
]
rbls["bl"]["osps.dnsbl.net.au"] = [
    "osps.dnsbl.net.au",
    "http://osps.dnsbl.net.au"
]
rbls["bl"]["osrs.dnsbl.net.au"] = [
    "osrs.dnsbl.net.au",
    "http://osrs.dnsbl.net.au"
]
rbls["bl"]["owfs.dnsbl.net.au"] = [
    "owfs.dnsbl.net.au",
    "http://owfs.dnsbl.net.au"
]
rbls["bl"]["owps.dnsbl.net.au"] = [
    "owps.dnsbl.net.au",
    "http://owps.dnsbl.net.au"
]
rbls["bl"]["pdl.dnsbl.net.au"] = [
    "pdl.dnsbl.net.au",
    "http://pdl.dnsbl.net.au"
]
rbls["bl"]["phishing-msrbl"] = [
    "phishing.rbl.msrbl.net",
    "http://www.msrbl.com/"
]
rbls["bl"]["probes.dnsbl.net.au"] = [
    "probes.dnsbl.net.au",
    "http://probes.dnsbl.net.au"
]
rbls["bl"]["proxy.bl.gweep.ca"] = [
    "proxy.bl.gweep.ca",
    "http://proxy.bl.gweep.ca"
]
rbls["bl"]["psbl.surriel.com"] = [
    "psbl.surriel.com",
    "http://psbl.surriel.com"
]
rbls["bl"]["pss.spambusters.org.ar"] = [
    "pss.spambusters.org.ar",
    "http://pss.spambusters.org.ar"
]
rbls["bl"]["rbl-plus.mail-abuse.org"] = [
    "rbl-plus.mail-abuse.org",
    "http://rbl-plus.mail-abuse.org"
]
rbls["bl"]["rbl.cluecentral.net"] = [
    "rbl.cluecentral.net",
    "http://rbl.cluecentral.net"
]
rbls["bl"]["rbl.efnet.org"] = [
    "rbl.efnet.org",
    "http://rbl.efnet.org"
]
rbls["bl"]["rbl.jp"] = [
    "rbl.jp",
    "http://rbl.jp"
]
rbls["bl"]["rbl.maps.vix.com"] = [
    "rbl.maps.vix.com",
    "http://www.mail-abuse.org/rbl/"
]
rbls["bl"]["rbl.schulte.org"] = [
    "rbl.schulte.org",
    "http://rbl.schulte.org"
]
rbls["bl"]["rbl.snark.net"] = [
    "rbl.snark.net",
    "http://rbl.snark.net"
]
rbls["bl"]["rbl.triumf.ca"] = [
    "rbl.triumf.ca",
    "http://rbl.triumf.ca"
]
rbls["bl"]["rdts.dnsbl.net.au"] = [
    "rdts.dnsbl.net.au",
    "http://rdts.dnsbl.net.au"
]
rbls["bl"]["relays.bl.gweep.ca"] = [
    "relays.bl.gweep.ca",
    "http://relays.bl.gweep.ca"
]
rbls["bl"]["relays.bl.kundenserver.de"] = [
    "relays.bl.kundenserver.de",
    "http://relays.bl.kundenserver.de"
]
rbls["bl"]["relays.mail-abuse.org"] = [
    "relays.mail-abuse.org",
    "http://work-rss.mail-abuse.org/rss/"
]
rbls["bl"]["relays.nether.net"] = [
    "relays.nether.net",
    "http://relays.nether.net"
]
rbls["bl"]["relays.nthelp.com"] = [
    "relays.nthelp.com",
    "http://relays.nthelp.com"
]
#rbls["bl"]["relays.radparker.com"] = [
#    "relays.radparker.com",
#    "http://relays.radparker.com/"
#]
rbls["bl"]["rhsbl.sorbs.net"] = [
    "rhsbl.sorbs.net",
    "http://www.dnsbl.nl.sorbs.net/"
]
rbls["bl"]["ricn.dnsbl.net.au"] = [
    "ricn.dnsbl.net.au",
    "http://ricn.dnsbl.net.au"
]
rbls["bl"]["rmst.dnsbl.net.au"] = [
    "rmst.dnsbl.net.au",
    "http://rmst.dnsbl.net.au"
]
rbls["bl"]["rsbl.aupads.org"] = [
    "rsbl.aupads.org",
    "http://rsbl.aupads.org"
]
rbls["bl"]["satos.rbl.cluecentral.net"] = [
    "satos.rbl.cluecentral.net",
    "http://satos.rbl.cluecentral.net"
]
rbls["bl"]["sbl-xbl.spamhaus.org"] = [
    "sbl-xbl.spamhaus.org",
    "http://sbl-xbl.spamhaus.org"
]
rbls["bl"]["sbl.csma.biz"] = [
    "sbl.csma.biz",
    "http://bl.csma.biz/"
]
rbls["bl"]["sbl.spamhaus.org"] = [
    "sbl.spamhaus.org",
    "http://www.spamhaus.org/sbl/"
]
rbls["bl"]["smtp.dnsbl.sorbs.net"] = [
    "smtp.dnsbl.sorbs.net",
    "http://www.dnsbl.nl.sorbs.net/"
]
rbls["bl"]["socks.dnsbl.sorbs.net"] = [
    "socks.dnsbl.sorbs.net",
    "http://www.dnsbl.nl.sorbs.net/"
]
rbls["bl"]["sorbs.dnsbl.net.au"] = [
    "sorbs.dnsbl.net.au",
    "http://sorbs.dnsbl.net.au"
]
rbls["bl"]["spam.dnsbl.sorbs.net"] = [
    "spam.dnsbl.sorbs.net",
    "http://www.dnsbl.nl.sorbs.net/"
]
rbls["bl"]["spam.dnsrbl.net"] = [
    "spam.dnsrbl.net",
    "http://spam.dnsrbl.net"
]
rbls["bl"]["spam.olsentech.net"] = [
    "spam.olsentech.net",
    "http://spam.olsentech.net"
]
rbls["bl"]["spam.wytnij.to"] = [
    "spam.wytnij.to",
    "http://spam.wytnij.to"
]
rbls["bl"]["spamcop"] = [
    "bl.spamcop.net",
    "http://www.spamcop.net/bl.shtml"
]
rbls["bl"]["spamguard.leadmon.net"] = [
    "spamguard.leadmon.net",
    "http://spamguard.leadmon.net"
]
rbls["bl"]["spamsites.dnsbl.net.au"] = [
    "spamsites.dnsbl.net.au",
    "http://spamsites.dnsbl.net.au"
]
rbls["bl"]["spamsources.dnsbl.info"] = [
    "spamsources.dnsbl.info",
    "http://spamsources.dnsbl.info"
]
rbls["bl"]["spamsources.fabel.dk"] = [
    "spamsources.fabel.dk",
    "http://spamsources.fabel.dk"
]
rbls["bl"]["spews.dnsbl.net.au"] = [
    "spews.dnsbl.net.au",
    "http://spews.dnsbl.net.au"
]
rbls["bl"]["t1.dnsbl.net.au"] = [
    "t1.dnsbl.net.au",
    "http://www.dnsbl.net.au/t1/"
]
rbls["bl"]["ucepn.dnsbl.net.au"] = [
    "ucepn.dnsbl.net.au",
    "http://ucepn.dnsbl.net.au"
]
rbls["bl"]["virbl"] = [
    "virbl.dnsbl.bit.nl",
    "https://virbl.bit.nl/faq.php"
]
rbls["bl"]["virus-msrbl"] = [
    "virus.rbl.msrbl.net",
    "http://www.msrbl.com/"
]
rbls["bl"]["virus.rbl.jp"] = [
    "virus.rbl.jp",
    "http://virus.rbl.jp"
]
rbls["bl"]["web.dnsbl.sorbs.net"] = [
    "web.dnsbl.sorbs.net",
    "http://www.dnsbl.nl.sorbs.net/"
]
rbls["bl"]["whois.rfc-ignorant.org"] = [
    "whois.rfc-ignorant.org",
    "http://whois.rfc-ignorant.org"
]
rbls["bl"]["will-spam-for-food.eu.org"] = [
    "will-spam-for-food.eu.org",
    "http://will-spam-for-food.eu.org"
]
rbls["bl"]["xbl.spamhaus.org"] = [
    "xbl.spamhaus.org",
    "http://www.spamhaus.org/xbl/"
]
rbls["bl"]["zombie.dnsbl.sorbs.net"] = [
    "zombie.dnsbl.sorbs.net",
    "http://www.dnsbl.nl.sorbs.net/"
]

from socket    import gethostbyaddr
from socket    import gethostbyname, gaierror
from time      import time, sleep
from Queue     import Queue, Empty
from threading import Thread
import re
from gozerbot.commands      import cmnds
from gozerbot.generic       import rlog
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.users         import users
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp

plughelp.add('rblcheck', 'check blacklists')

cfg = PersistConfig()
cfg.define('throttle', 60)
cfg.define('max-threads', 5)
cfg.define('debug', 0)
debug = 0

def list_check(list, chkip):
    results = []
    for i in list.keys():
        chk = "%s.%s" % (".".join(reversed(chkip.split("."))), list[i][0])
        try: qr = gethostbyname("%s" % (chk))
        except: qr = None
        if qr:
            results.append(list[i])
            if cfg.get('debug'):
                rlog(10, 'rblcheck', '%s result: %s' % (chk, str(qr)))
    return results

class pool_check(object):

    timeout = 1.0

    def __init__(self, lookups, ip):
        self.cip = ip
        self.rip = ".".join(reversed(self.cip.split(".")))
        self.todo = Queue()
        self.hits = Queue()
        self.pool = []
        self.fill(lookups)

    def fill(self, lookups):
        # propagate todo queue
        for lookup in lookups:
            self.todo.put([lookup, lookups[lookup]])

    def run(self):
        # start runner threads
        for i in xrange(0, cfg.get('max-threads')):
            runner = Thread(target=self.poll)
            runner.start()
            self.pool.append(runner)
        # now we wait until all runners in the pool are done
        while True:
            if not self.pool:
                break
            sleep(self.timeout)
        hits = []
        while True:
            try: hits.append(self.hits.get(block=False, timeout=0.01))
            except Empty: break
        return hits

    def poll(self):
        while True:
            try:
                item, info = self.todo.get(block=False, timeout=self.timeout)
                try: listed = gethostbyname("%s.%s" % (self.rip, item))
                except gaierror: listed = False
                if listed: self.hits.put(info)
            except Empty:
                break # no more items in queue
        self.pool.pop(0) # remove item from queue

class RBLCheck(object):
    
    re_ip = re.compile('^(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    throttle = {}

    def handle_rblcheck(self, bot, ievent):
        if not self.re_ip.match(ievent.rest.strip()):
            ievent.missing('<ip>')
            return
        user = users.getname(ievent.userhost)
        if self.throttle.has_key(user) and self.throttle[user] >= time():
            ievent.reply('throttled - you can only do one lookup each %d seconds' % cfg.get('throttle'))
            return
        self.throttle[user] = time() + cfg.get('throttle')
        ip = ievent.rest.strip()
        ievent.reply('checking %d blacklists' % len(rbls['bl']))
        checks = pool_check(rbls['bl'], ip)
        result = checks.run()
        #result = list_check(rbls['bl'], ip)
        if result:
            results = []
            for r in result:
                results.append('%s (%s)' % (r[0], r[1]))
            ievent.reply('%s is blacklisted: ' % ip, results)
        else:
            ievent.reply('%s is not blacklisted' % ip)

rblcheck = RBLCheck()
cmnds.add('rblcheck', rblcheck.handle_rblcheck, 'USER')
examples.add('rblcheck', 'check <ip> with blacklists', 'rblcheck 127.0.0.1')

