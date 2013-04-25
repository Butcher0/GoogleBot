'''
Created on 25. apr. 2013

@author: avenes
'''


import sys
import logging
import getpass
from optparse import OptionParser

import sleekxmpp



class EchoBot(sleekxmpp.ClientXMPP):
    
    def __init__(self,jid,password):
        sleekxmpp.ClientXMPP.__init__(self,jid,password)
        self.add_event_handler('session_start',self.start)
        self.add_event_handler('message',self.message)


    def start(self,event):
        self.send_presence()
        self.get_roster()
    
    
    def message(self, msg):
        if msg['type'] in ('normal', 'chat'):
            msg.reply("Takka for at du sendte meg info: \n%(body)s" % msg).send()
            

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
    
    xmpp = EchoBot(opts.jid, opts.password)
    xmpp.register_plugin('xep_0030')
    xmpp.register_plugin('xep_0199')
    
    if xmpp.connect(('talk.google.com', '5222')):
        xmpp.process(block=True)
    else:
        print('Fekk ikkje kopla til')
        
        