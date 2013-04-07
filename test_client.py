#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
try:
    from twisted.internet import epollreactor
    epollreactor.install()
except:
    pass

from twisted.internet import protocol, reactor
from twisted.protocols.basic import Int32StringReceiver
import time
import threading

class ConsoleClient(Int32StringReceiver):
    clients = []
    latencies = []
    i = 0
    def connectionMade(self):
        self.n = ConsoleClient.i
        ConsoleClient.i += 1
        self.t = time.time()
        self.queue = 0

    def stringReceived(self, line):
        t = time.time()
        print t-self.t
        print line
        ConsoleClient.latencies.append(t-self.t)
        if self.queue:
            self.queue -= 1
            self.send_message()

    def startConsole(self):
        exitCmd = ['exit', 'quit', 'done']
        print "Enter the messages you want to send to the server"
        print 'Example: {"type": "whoami", "args":{}})'
        print "To exit, type exit, quit, or done"
        message = raw_input()
        while (message not in exitCmd):
            self.sendString(message)
            message = raw_input()
        reactor.stop()

def protocol_created(p):
    ConsoleClient.clients.append(p)
    consoleThread = threading.Thread(target=ConsoleClient.startConsole, args=(p,))
    consoleThread.start()

def start_sessions():
    cc = protocol.ClientCreator(reactor, ConsoleClient)
    d = cc.connectTCP("127.0.0.1", 19000)
    d.addCallback(protocol_created)
    #reactor.callLater(0, cc.startConsole())

reactor.callLater(0, start_sessions)
reactor.run()
