# -*- coding: iso-8859-1 -*-

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
            error = {'type': 'parse error'}
            error['message'] = string
            self.send_json(error)
            return
        self.app.run(expr)

    def send_json(self, object):
        message = json.dumps(object)
        self.sendString(message)
