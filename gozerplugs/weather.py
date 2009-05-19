""" show weather based on Google's weather API """

__copyright__ = 'this file is in the public domain'
__author__ = 'Landon Fowles'

from gozerbot.generic import geturl, waitforuser, getwho, rlog
from gozerbot.commands import cmnds
from gozerbot.datadir import datadir
from gozerbot.persist.persist import Persist
from gozerbot.users import users
from gozerbot.plughelp import plughelp
from gozerbot.examples import examples
from gozerbot.persist.persiststate import UserState
from gozerbot.aliases import aliasset
import time
from xml.dom import minidom
from urllib import urlencode

plughelp.add('weather', 'show weather by zipcode/city name')

def handle_weather(bot, ievent):
    """ show weather using Google's weather API """
    userhost = ""
    loc = ""
    try:
        nick = ievent.options['--u']
        if nick:
            userhost = getwho(bot, nick)
            if not userhost:
                ievent.reply("can't determine username for %s" % nick)
                return
            else:
                try:
                    name = users.getname(userhost)
                    if not name:
                         ievent.reply("%s is not known with the bot" % nick)
                         return
                    us = UserState(name)
                    loc = us['location']
                except KeyError:
                    ievent.reply("%s doesn't have his location set in \
userstate" % nick)
                    return
    except KeyError:
         pass
    if not loc:
        if ievent.rest:
             loc = ievent.rest
        else:
             ievent.missing('--u <nick> or <location>')
             return
    query = urlencode({'weather':loc})
    weathertxt = geturl('http://www.google.ca/ig/api?%s' % query)
    if 'problem_cause' in weathertxt:
        rlog(10, 'weather', 'ERROR: %s' % weathertxt)
        ievent.reply('an error occured looking up data for %s' % loc)
        return
    resultstr = ""
    if len(weathertxt) > 135:
        gweather = minidom.parseString(weathertxt)
        gweather = gweather.getElementsByTagName('weather')[0]
        if ievent.command == "weather":
            info = gweather.getElementsByTagName('forecast_information')[0]
            if info:
                city = info.getElementsByTagName('city')[0].attributes["data"].value
                zip = info.getElementsByTagName('postal_code')[0].attributes["data"].value
                time = info.getElementsByTagName('current_date_time')[0].attributes["data"].value

                weather = gweather.getElementsByTagName('current_conditions')[0]
                condition = weather.getElementsByTagName('condition')[0].attributes["data"].value
                temp_f = weather.getElementsByTagName('temp_f')[0].attributes["data"].value
                temp_c = weather.getElementsByTagName('temp_c')[0].attributes["data"].value
                humidity = weather.getElementsByTagName('humidity')[0].attributes["data"].value
                wind = weather.getElementsByTagName('wind_condition')[0].attributes["data"].value

                try:
                    wind_km = round(int(wind[-6:-4]) * 1.609344)
                except ValueError:
                    wind_km = ""

                if (not condition == ""):
                    condition = " Oh, and it's " + condition + "."

                resultstr = "As of %s, %s (%s) has a temperature of %sC/%sF with %s. %s (%s km/h).%s" % (time, city, zip, temp_c, temp_f, humidity, wind, wind_km, condition)
        elif ievent.command == "forecast":
            forecasts = gweather.getElementsByTagName('forecast_conditions')
            for forecast in forecasts:
                condition = forecast.getElementsByTagName('condition')[0].attributes["data"].value
                low_f = forecast.getElementsByTagName('low')[0].attributes["data"].value
                high_f = forecast.getElementsByTagName('high')[0].attributes["data"].value
                day = forecast.getElementsByTagName('day_of_week')[0].attributes["data"].value
                low_c = round((int(low_f) - 32) * 5.0 / 9.0)
                high_c = round((int(high_f) - 32) * 5.0 / 9.0)
                resultstr += "[%s: F(%sl/%sh) C(%sl/%sh) %s]" % (day, low_f, high_f, low_c, high_c, condition)
    if not resultstr:
        ievent.reply('%s not found!' % loc)
        return
    else:
        ievent.reply(resultstr)

cmnds.add('weather', handle_weather, 'USER', options={'--u': ''})
aliasset('forecast', 'weather')
examples.add('weather', 'get weather for <LOCATION> or <nick>', '1) weather London, \
England 2) weather dunker')
