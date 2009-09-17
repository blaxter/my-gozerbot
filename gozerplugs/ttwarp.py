# encoding: utf-8

from gozerbot.commands import cmnds
import socket
from htmlentitydefs import name2codepoint as n2cp
import re
import httplib2
import random
import urllib
from time import strftime
import datetime
import time

# Here, there are all constants needed with hardcoded passwords
# Also there is a h variable, instance of httplib2
from ttwarp_data import *

def substitute_entity(match):
   ent = match.group(2)
   try:
      if match.group(1) == "#":
         return unichr(int(ent))
      else:
         cp = n2cp.get(ent)
      if cp:
         return unichr(cp)
      else:
         return match.group()
   except UnicodeDecodeError:
      return ent

def decode_htmlentities(string):
    #return string
   entity_re = re.compile("&(#?)(\d{1,5}|\w{1,8});")
   return entity_re.subn(substitute_entity, string)[0]

def get_login(user=DEFAULT_USER):
   url_login = BASE_URL + '/login/login'
   body = {'user[name]': LOGINS[user]['user'], 'user[prepasswd]': LOGINS[user]['password'] }
   headers = {'Content-type': 'application/x-www-form-urlencoded'}
   response, content = h.request(url_login, 'POST', headers=headers, body=urllib.urlencode(body))
   return response['set-cookie']

def get(url, user=DEFAULT_USER):
   headers = {'Cookie': get_login(user)}
   response, content = h.request(BASE_URL + url, headers=headers)
   while response['status'] == '302':
      headers = { 'Cookie': response['set-cookie'] }
      response, content = h.request(response['location'], headers=headers)
   return response, content

def is_logged():
   resp, content = get("/timetracking/hq")
   return re.search(NAME_IN_HQ, content) != None

def get_adage():
   resp, content = get("/timetracking/punch/punch_in")

   adage = re.search('<p\s+class="adage_message"\s*>((.|\n)+)<p class="adage_creator"', content).group(1)[:-9]
   adage = decode_htmlentities(adage)

   creator = re.search('<p class="adage_creator">(.+)</p>', content).group(1)

   author = re.search('<p class="adage_author">(.+)</p>', content)
   if author: author = author.group(1)

   months_adage = False
   status       = 'Desconocido'
   status = re.search('<span class="adage_karma_info">\n\s+((.|\n)+)</span>', content)
   if status:
      status = re.sub('\n$', '', re.sub('\n\s+', '\n', status.group(1)))
   else:
      status = re.search('<div class="months_adage">\n\s+(([^<])+)<', content)
      if status:
         status = re.sub('\n$', '', re.sub('\n\s+', '\n', status.group(1)))
         months_adage = True
      else:
         status = '¡No hay puntuación!'

   if months_adage:
      month = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%B del %Y")
      adage = "¡Adagio del mes de "+ month +"! \n" + adage
   return adage, creator, author, status

def adage():
   adagio = ["No puedo ver el adagio porque no estoy currando :o"]
   if is_logged():
      adage, creator, author, status = get_adage()
      if author:
         adagio = (adage + "\n" + "by: " + author).split("\n")
      else:
         adagio = adage.split("\n")
   return adagio

def get_adage_author():
   if is_logged():
      adage, creator, author, status = get_adage()
      return creator
   else:
      return False

def adage_author():
   if is_logged():
      adage, creator, author, status = get_adage()
      return ["Enviado por " + creator]
   else:
      return ["No puedo ver el adagio porque no estoy currando :o"]

def adage_score():
   if is_logged():
      adage, creator, author, status = get_adage()
      return ("Estado: " + status ).split("\n")
   else:
      return ["No puedo ver el adagio porque no estoy currando :o"]

def vote_up(user=DEFAULT_USER):
   if strftime("%d") == '01':
      return ["Hoy es el adagio del mes, no puedes votar co"]
   else:
     resp, content = get("/timetracking/adage/up", user)
     return ["votado positivo"]

def vote_down(user=DEFAULT_USER):
   if strftime("%d") == '01':
      return ["Hoy es el adagio del mes, no puedes votar co"]
   else:
      resp, content = get("/timetracking/adage/down", user)
      return ["votado negativo"]

def punch_in(user):
   if LOGINS[user].has_key('disabled') and LOGINS[user]['disabled']:
      return ['tu no puedes hacer punch in, ' + LOGINS[user]['foo']]
   resp, content = get("/timetracking/punch/punch_in", user)
   warning = getwarnings(content)
   if warning:
      return [warning]
   else:
      adage_regex = re.search('<p\s+class="adage_message"\s*>((.|\n)+)<p class="adage_creator"', content)
      if adage_regex.group(1):
         return ["¡Puncheado " + user + "!"]
      else:
         return ["Algo raro ha pasado co"]

def punch_out(user):
   if LOGINS[user].has_key('disabled') and LOGINS[user]['disabled']:
      return ['tu no puedes hacer punch out, ' + LOGINS[user]['foo']]
   resp, content = get("/timetracking/punch/punch_out", user)
   warning = getwarnings(content)
   if warning:
      return [warning]
   else:
      return ["¡Punchouteado " + user + "!"]

def getwarnings(content):
   war_regex = re.search('<div\s+class="warning"\s*>((.)+)</div>', content)
   if war_regex and war_regex.group(1):
      return war_regex.group(1)

   war_regex = re.search('<div\s+id="warning"\s*>((.)+)</div>', content)
   if war_regex and war_regex.group(1):
      return war_regex.group(1)

   war_regex = re.search('<div\s+class="message"\s*>((.)+)</div>', content)
   if war_regex and war_regex.group(1):
      return war_regex.group(1)

   war_regex = re.search('<div\s+id="message"\s*>((.)+)</div>', content)
   if war_regex and war_regex.group(1):
      return war_regex.group(1)

   return False

################################################################################

def _punch_request(user, punch_in_or_out):
    if LOGINS.has_key(user):
        if punch_in_or_out:
            return punch_in(user)
        else:
            return punch_out(user)

def _adage_request():
    return adage()

def _author_request():
    return adage_author()

def _score_request():
    return adage_score()

def _vote_adage_request(user, up_or_down):
    if LOGINS.has_key(user):
        if up_or_down:
            response = vote_up( user )
        else:
            response = vote_down( user )
    else:
        response = [ "User no valid co" ]
    return response

def _guess(author_guess):
    author = get_adage_author()
    if author:
        if author == author_guess:
            return [ '¡Claramente, has acertado!' ]
        else:
            return [ '¡Te equivocas!  http://➡.ws/ßß ' ]
    else:
        return [ 'No puedo ver el adagio co' ]

# v handle_xxxxx methods -------------------------------------------------------

def error_socket( ievent ):
    ievent.reply( "Error en la conexión co, ya lo siento" )

def handle_adagio(bot, ievent):
    try:
        reply = _adage_request()
        print_reply( ievent, reply )
    except socket.error:
        error_socket( ievent )

def handle_author(bot, ievent):
    try:
        reply = _author_request()
        print_reply( ievent, reply )
    except socket.error:
        error_socket( ievent )

def handle_score(bot, ievent):
    try:
        reply = _score_request()
        print_reply( ievent, reply )
    except socket.error:
        error_socket( ievent )

def handle_guess(bot, ievent):
    try:
        if len(ievent.args) == 1:
            author = str( ievent.args[0] )

            reply = _guess( author )
            print_reply( ievent, reply )
    except socket.error:
        error_socket( ievent )

def handle_rocks(bot, ievent):
    try:
        reply = _vote_adage_request(ievent.nick, True)
        print_reply( ievent, reply )
    except socket.error:
        error_socket( ievent )

def handle_sucks(bot, ievent):
    try:
        reply = _vote_adage_request(ievent.nick, False)
        print_reply( ievent, reply )
    except socket.error:
        error_socket( ievent )

def handle_punch_in(bot, ievent):
    try:
        reply = _punch_request(ievent.nick, True)
        print_reply( ievent, reply )
    except socket.error:
        error_socket( ievent )

def handle_punch_out(bot, ievent):
    try:
        reply = _punch_request(ievent.nick, False)
        print_reply( ievent, reply )
    except socket.error:
        error_socket( ievent )


def print_reply(ievent, reply):
    if reply:
        for line in reply:
            ievent.reply( line )

cmnds.add('adagio', handle_adagio, 'ANY')
cmnds.add('author', handle_author, 'ANY')
cmnds.add('score', handle_score, 'ANY')
cmnds.add('guess', handle_guess, 'ANY')
cmnds.add('rocks', handle_rocks, 'ANY')
cmnds.add('sucks', handle_sucks, 'ANY')
cmnds.add('punchin', handle_punch_in, 'ANY')
cmnds.add('punchout', handle_punch_out, 'ANY')
