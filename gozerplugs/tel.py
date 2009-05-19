# plugs/tel.py
#
#

""" telefone codes """

__copyright__ = 'this file is in the public domain'

from gozerbot.generic import geturl, striphtml, splittxt
from gozerbot.commands import cmnds
from gozerbot.aliases import aliases
from gozerbot.examples import examples
from gozerbot.plughelp import plughelp
import re, random

plughelp.add('tel', 'show country telephone codes')

codes = [
	("213", "ALGERIA", "DZ"),
	("102", "ANTIGUA BARBUDA", ""),
	("54", "ARGENTINA", "AR"),
	("374", "ARMENIA", "AM"),
	("297", "ARUBA", "AW"),
	("61", "AUSTRALIA", "AU"),
	("43", "AUSTRIA", "AT"),
	("994", "AZERBAIJAN", "AZ"),
	("103", "BAHAMAS", "BS"),
	("104", "BARBADOS", "BB"),
	("375", "BELARUS", "BY"),
	("32", "BELGIUM", "BE"),
	("105", "BERMUDA", "BM"),
	("591", "BOLIVIA", "BO"),
	("55", "BRAZIL", "BR"),
	("673", "BRUNEI", ""),
	("359", "BULGARIA", "BG"),
	("107", "CANADA", "CA"),
	("108", "CAYMAN ISLANDS", ""),
	("38", "CHILE", "CL"),
	("57", "COLOMBIA", "CO"),
	("506", "COSTA RICA", ""),
	("53", "CUBA", "CU"),
	("357", "CYPRUS", "CY"),
	("420", "CZECHREPUBLIC", ""),
	("45", "DENMARK", "DK"),
	("593", "ECUADOR", "EC"),
	("20", "EGYPT", "EG"),
	("503", "EL SALVADOR", ""),
	("358", "FINLAND", "FI"),
	("33", "FRANCE", "FR"),
	("49", "GERMANY", "DE"),
	("30", "GREECE", "GR"),
	("111", "GRENADA", "GD"),
	("502", "GUATEMALA", "GT"),
	("592", "GUYANA", "GY"),
	("504", "HONDURAS", "HN"),
	("852", "HONG KONG", ""),
	("36", "HUNGARY", "HU"),
	("91", "INDIA", "IN"),
	("62", "INDONESIA", "ID"),
	("353", "IRELAND", "IE"),
	("972", "ISRAEL", "IL"),
	("39", "ITALY", "IT"),
	("112", "JAMAICA", "JM"),
	("81", "JAPAN", "JP"),
	("962", "JORDAN", "JO"),
	("850", "KOREA", ""),
	("82", "KOREA SOUTH", ""),
	("965", "KUWAIT", "KW"),
	("352", "LUXEMBOURG", "LU"),
	("60", "MALAYSIA", "MY"),
	("52", "MEXICO", "MX"),
	("599", "NETH ANTILLES", ""),
	("31", "NETHERLANDS", "NL"),
	("64", "NEW ZEALAND", ""),
	("505", "NICARAGUA", "NI"),
	("47", "NORWAY", "NO"),
	("968", "OMAN", "OM"),
	("92", "PAKISTAN", "PK"),
	("507", "PANAMA", "PA"),
	("595", "PARAGUAY", "PY"),
	("51", "PERU", "PE"),
	("63", "PHILIPPINES", "PH"),
	("48", "POLAND", "PL"),
	("351", "PORTUGAL", "PT"),
	("852", "PRC", ""),
	("40", "ROMANIA", "RO"),
	("7", "RUSSIA", ""),
	("966", "SAUDI ARABIA", ""),
	("65", "SINGAPORE", "SG"),
	("421", "SLOVAKIA", "SK"),
	("386", "SLOVENIA", "SI"),
	("27", "SOUTH AFRICA", ""),
	("34", "SPAIN", "ES"),
	("115", "ST KITTS NEVIS", ""),
	("122", "ST LUCIA", ""),
	("116", "ST VINCENT", ""),
	("597", "SURINAME", "SR"),
	("46", "SWEDEN", "SE"),
	("41", "SWITZERLAND", "CH"),
	("866", "TAIWAN", ""),
	("66", "THAILAND", "TH"),
	("117", "TRINIDAD TOBAGO", ""),
	("90", "TURKEY", "TR"),
	("118", "TURKS CAICOS", ""),
	("44", "UNITED KINGDOM", "UK"),
	("380", "UKRAINE", "UA"),
	("971", "UNITED ARAB EMIRATES", ""),
	("598", "URUGUAY", "UY"),
	("1", "UNITED STATES OF AMERICA", "USA"),
	("58", "VENEZUELA", "VE"),
	("84", "VIETNAM", ""),
	("106", "VIRGIN IS BRITISH", ""),
	("123", "VIRGIN IS USA", ""),
	("967", "YEMAN", ""),
	("381", "YUGOSLAVIA", ""),
	("666", "NUMBER OF THE BEAST", ""),
]

def handle_tel(bot, ievent):
    if not ievent.rest:
        ievent.missing('<what>')
        return
    l = ievent.rest.upper()
    res = None
    for c in codes:
	if l in c:
	    res = "%s has dialing prefix %s" % (c[1], c[0])
	    break
    if not res:
	# match part of
	for c in codes:
	    if l in c[1]:
		res = "%s has dialing prefix %s" % (c[1], c[0])
		break
    if not res:
	res = "%s not found" % l
    ievent.reply(res)

cmnds.add('tel', handle_tel, 'USER')
examples.add('tel', 'show country telephone code', 'tel 31')
