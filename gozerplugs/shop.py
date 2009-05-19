# plugs/shop.py
#
#

__copyright__ = 'this file is in the public domain'
__gendocfirst__ = ['shop', ]

from gozerbot.utils.generic import convertpickle
from gozerbot.generic import getwho, jsonstring
from gozerbot.users import users
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.datadir import datadir
from gozerbot.persist.pdol import Pdol
from gozerbot.plughelp import plughelp
import os

plughelp.add('shop', ' maintain shopping lists per user')

## UPGRADE PART

def upgrade():
    convertpickle(datadir + os.sep + 'old' + os.sep + 'shops',  datadir + os.sep + 'plugs' + \
os.sep + 'shop' + os.sep + 'shops')

## END UPGRADE PART

shops = Pdol(datadir + os.sep + 'plugs' + os.sep + 'shop' + os.sep + 'shops')

## END UPGRADE PART

def size():
    """ return number of shops entries """
    return len(shops.data)

def sayshop(bot, ievent, shoplist):
    """ output shoplist """
    if not shoplist:
        ievent.reply('nothing to shop ;]')
        return
    result = []
    teller = 0
    for i in shoplist:
        result.append('%s) %s' % (teller, i))
        teller += 1
    ievent.reply("shoplist: ", result)

def handle_shop(bot, ievent):
    """ shop [<item>] .. show shop list or add <item> """
    if len(ievent.args) != 0:
        handle_shop2(bot, ievent)
        return
    shop = []
    username = users.getname(ievent.userhost)
    shop = shops[username]
    sayshop(bot, ievent, shop)

cmnds.add('shop', handle_shop, 'USER')

def handle_shop2(bot, ievent):
    """ add items to shop list """
    if not ievent.rest:
        ievent.missing('<shopitem>')
        return
    else:
        what = ievent.rest
    username = users.getname(ievent.userhost)
    shops[username] = what
    shops.save()
    ievent.reply('shop item added')

examples.add('shop', 'shop [<item>] .. show shop items or add a shop item', \
'1) shop 2) shop bread')

def handle_shopchan(bot, ievent):
    """ shop-chan [<item>] .. show channel shop list or add <item> """
    if len(ievent.args) != 0:
        handle_shopchan2(bot, ievent)
        return
    shop = shops[jsonstring((bot.name, ievent.channel))]
    sayshop(bot, ievent, shop)

cmnds.add('shop-chan', handle_shopchan, 'USER')
examples.add('shop-chan', 'shop-chan [<item>] .. show channel shop list or \
add <item>', '1) shop-chan 2) shop-chan milk')

def handle_shopchan2(bot, ievent):
    """ add items to shop list """
    if not ievent.rest:
        ievent.missing('<shopitem>')
        return
    else:
        what = ievent.rest
    shops[jsonstring((bot.name, ievent.channel))] = what
    shops.save()
    ievent.reply('shop item added')

def handle_addshop(bot, ievent):
    """ shop-add <username> <item> .. add items to shop list of <username>"""
    if len(ievent.args) < 2:
        ievent.missing('<username> <item>')
        return
    else:
        who = ievent.args[0]
        what = ' '.join(ievent.args[1:])
    userhost = getwho(bot, who)
    if not userhost:
        ievent.reply("can't find userhost of %s" % who)
        return
    # get username of use giviing the command
    username = users.getname(ievent.userhost)
    # get username of person we want to knwo the shop list of
    whoname = users.getname(userhost)
    if not whoname:
        ievent.reply("can't find user for %s" % userhost)
        return
    if users.permitted(userhost, username, 'shop'):
        shops[whoname] = what
        shops.save()
        ievent.reply('shop item added')
    else:
        ievent.reply("%s does not share shopping list with %s" % (who, \
username))

cmnds.add('shop-add', handle_addshop, 'USER')
examples.add('shop-add', 'shop-add <username> <item> .. add shop item of \
someone else', '1) shop-add test milk')

def handle_getshop(bot, ievent):
    """ shop-get <name> .. get items of someone elses shop list """
    if not ievent.rest:
        ievent.missing('<username>')
        return
    who = ievent.rest
    userhost = getwho(bot, who)
    if not userhost:
        ievent.reply("can't find userhost of %s" % who)
        return
    username = users.getname(ievent.userhost)
    whoname = users.getname(userhost)
    if not whoname:
        ievent.reply("can't find user for %s" % userhost)
        return
    if users.permitted(userhost, username, 'shop'):
        shop = shops[whoname]
        sayshop(bot, ievent, shop)
    else:
        ievent.reply("%s does not share shopping list with %s" % (who, \
username))

cmnds.add('shop-get', handle_getshop, ['USER', 'WEB'])
examples.add('shop-get', 'shop-get <name> .. get shop items of someone \
else', '1) shop-get test')

def handle_delshop(bot, ievent):
    """ shop-del <username> <listofnrs> .. delete items of someone elses \
        shop list """
    if len(ievent.args) < 2:
        ievent.missing('<username> <listofnrs>')
        return
    else:
        who = ievent.args[0]
    try:
        nrs = []
        for i in ievent.args[1:]:
            nrs.append(int(i))
    except ValueError:
        ievent.reply('%s is not an integer' % i)
        return
    userhost = getwho(bot, who)
    if not userhost:
        ievent.reply("can't find userhost of %s" % who)
        return
    username = users.getname(ievent.userhost)
    whoname = users.getname(userhost)
    if not whoname:
        ievent.reply("can't find user for %s" % userhost)
        return
    if users.permitted(userhost, username, 'shop'):
        try:
            shop = shops[whoname]
        except KeyError:
            ievent.reply('nothing to shop ;]')
            return
        nrs.sort()
        nrs.reverse()
        for i in range(len(shop)-1, -1 , -1):
            if i in nrs:
                try:
                    del shop[i]
                except IndexError:
                    pass
        shops.save()
        ievent.reply('shop item deleted')
    else:
        ievent.reply("%s does not share shopping list with %s" % (who, \
username))

cmnds.add('shop-del', handle_delshop, 'USER')
examples.add('shop-del', 'shop-del <username> <listofnrs> .. delete shop \
item of someone else', '1) shop-del test 2 4 5')

def handle_got(bot, ievent):
    """ got <listofnrs> .. remove items from shoplist """
    if len(ievent.args) == 0:
        ievent.missing('<list of nrs>')
        return
    try:
        nrs = []
        for i in ievent.args:
            nrs.append(int(i))
    except ValueError:
        ievent.reply('%s is not an integer' % i)
        return
    username = users.getname(ievent.userhost)
    try:
        shop = shops[username]
    except KeyError:
        ievent.reply('nothing to shop ;]')
        return
    if not shop:
        ievent.reply("nothing to shop ;]")
        return
    nrs.sort()
    nrs.reverse()
    teller = 0
    for i in range(len(shop)-1, -1 , -1):
        if i in nrs:
            try:
                del shop[i]
                teller += 1
            except IndexError:
                pass
    shops.save()
    ievent.reply('%s shop item(s) deleted' % teller)

cmnds.add('got', handle_got, 'USER')
examples.add('got', 'got <listofnrs> .. remove item <listofnrs> from shop \
list','1) got 3 2) got 1 6 8')

def handle_gotchan(bot, ievent):
    """ got-chan <listofnrs> .. remove items from channel shoplist """
    if len(ievent.args) == 0:
        ievent.missing('<list of nrs>')
        return
    try:
        nrs = []
        for i in ievent.args:
            nrs.append(int(i))
    except ValueError:
        ievent.reply('%s is not an integer' % i)
        return
    try:
        shop = shops[jsonstring((bot.name, ievent.channel))]
    except KeyError:
        ievent.reply("nothing to shop")
        return
    if not shop:
        ievent.reply("nothing to shop")
        return
    nrs.sort()
    nrs.reverse()
    teller = 0
    for i in range(len(shop)-1, -1 , -1):
        if i in nrs:
            try:
                del shop[i]
                teller += 1
            except IndexError:
                pass
    shops.save()
    ievent.reply('%s shop item(s) deleted' % teller)

cmnds.add('got-chan', handle_gotchan, 'USER')
examples.add('got-chan', 'got-chan <listofnrs> .. remove listofnrs from \
channel shop list', '1) got-chan 3 2) got-chan 1 6 8')
