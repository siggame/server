# -*- coding: iso-8859-1 -*-

from twisted.internet import epollreactor
epollreactor.install()

from twisted.internet import protocol, reactor
from twisted.protocols.basic import Int32StringReceiver

import json
import apps

class JSONProtocol(Int32StringReceiver):
    app = apps.LoginApp

    def connectionMade(self):
        self.app = self.__class__.app(self)

    def connectionLost(self, reason):
        self.app.disconnect(reason)

    def stringReceived(self, string):
        try:
            expr = json.loads(string)
        except:
            print 'Bad message received: %s' % string
        for command in expr:
            self.app.run(command)

    @classmethod
    def main(cls, port=19000):
        f = protocol.ServerFactory()
        f.protocol = cls
        reactor.listenTCP(port, f)
        reactor.run()
