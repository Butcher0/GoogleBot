'''
Created on 25. apr. 2013

@author: avenes
'''



from optparse import OptionParser

import getpass
import logging
import re
import sleekxmpp
#import psutil
import time
import urllib.request
import json
from pprint import pprint
from urllib.parse import urlencode

startTime = time.time()

class AreBot(sleekxmpp.ClientXMPP):
    

    def __init__(self,jid,password):
        sleekxmpp.ClientXMPP.__init__(self,jid,password)
        self.add_event_handler('session_start',self.start)
        self.add_event_handler('message',self.message)


    def getUptime(self, msg):
        upTime = time.time() - startTime
        if(upTime<60):
            msg.reply('Boten har oppetid ' + str('%.2f' % upTime) + ' sekunder').send()
        elif(upTime/60 < 60):
            upTime = upTime/60
            msg.reply('Boten har oppetid ' + str('%.2f' % upTime) + ' minutter').send()
        else:
            upTime = upTime/60/60
            msg.reply('Boten har oppetid ' + str('%.2f' % upTime) + ' timer').send()

    def getWeather(self, city, msg):
#        root = "http://openweathermap.org/data/2.1/forecast/city?q=bergen"

        root = "http://api.openweathermap.org/data/2.5/weather?q=" + urllib.parse.quote(city.encode('utf-8'))
        response = urllib.request.urlopen(root)
        jsonResponse = json.loads(response.read().decode())

        msg.reply("Weather in: " + jsonResponse["name"] + '\n' + "Mainly: " + jsonResponse["weather"][0]["main"] + '\n' 
                  + "Description: " + jsonResponse["weather"][0]["description"] + '\n' 
                  + "Minimum temp: " + str('%.2f' % (jsonResponse["main"]["temp_min"]- 273.15)) + " C" + '\n'
                  + "Maximum temp: " + str('%.2f' % (jsonResponse["main"]["temp_max"]- 273.15)) + " C" + '\n'
                  + "Wind speed: " + str(jsonResponse["wind"]["speed"]) + " m/s").send()

        
    def start(self,event):
        self.send_presence()
        self.get_roster()
    
    def respNo(self,msg):
        msg.reply("NEI!").send()
        
    
    def respGreeting(self,msg):
        msg.reply("Heisan").send()
        
    def authenticateUser(self,user, msg):
#       expand to fetch list of admins from external source
        if (msg['body'] in ('whoami') and (user == 'arevenes@gmail.com')):
            return 'admin'
        elif(msg['body'] in ('whoami') and (user != 'arevenes@gmail.com')):
            return 'regular'
        if(user == 'arevenes@gmail.com'):
            msg.reply('You are authenticated as admin user').send()
            return 'admin'
        else: msg.reply('You are authenticated as regular user').send()
        return 'regular'
    
    
    def message(self, msg):
        
#       expand to use regex user@usermail/ 
        user = str(msg['from'])
        user = user[:-15]

        if msg['type'] in ('normal', 'chat') and re.match('(.*)\?', msg['body'], 0):
            self.respNo(msg)
#            msg.reply("Takka for at du sendte meg info: \n%(body)s" % msg).send()
#            msg.reply("jau god kvelden" % msg).send()

        if msg['type'] in ('normal', 'chat') and msg['body'] in ('usermode'):
            self.authenticateUser(user, msg)
        
        if msg['type'] in ('normal', 'chat') and msg['body'] in ('whoami'):
            msg.reply(self.authenticateUser(user, msg)).send()
                
        
        if msg['type'] in ('normal', 'chat') and msg['body'] in ('hallo','god dag'):
            self.respGreeting(msg)

        if msg['type'] in ('normal', 'chat') and msg['body'] in ('uptime'):
            self.getUptime(msg)

#       fix such that cities with two words (New York) works as supposed (new%20york) 
        if msg['type'] in ('normal', 'chat') and re.match('(var)\_', msg['body'], 0): #and msg['body'] in ('ver'):
            city = msg['body'][4:]
            print(city)
            self.getWeather(city, msg)
            

if __name__ == '__main__':
    optp = OptionParser()

    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")

    opts, args = optp.parse_args()

    if opts.jid is None:
        opts.jid = input("Username: ")
    if opts.password is None:
        opts.password = getpass.getpass("Password: ")
    
    logging.basicConfig(level=opts.loglevel,format='%(levelname) -8s %(message)s')
    
    xmpp = AreBot(opts.jid, opts.password)
    xmpp.register_plugin('xep_0030')
    xmpp.register_plugin('xep_0199')
    
    if xmpp.connect(('talk.google.com', '5222')):
        xmpp.process(block=True)
    else:
        print('Fekk ikkje kopla til')
        
        