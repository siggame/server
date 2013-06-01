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
            self.send_message('parse error', message=string, reason='failed to parse as json')
            return
        if not isinstance(expr, dict):
            self.send_message('parse error', message=string, reason='commands must be objects')
        elif 'type' not in expr or not isinstance(expr['type'], basestring):
            self.send_message('parse error', message=string, reason='commands must contain type string')
        elif 'args' not in expr or not isinstance(expr['args'], dict):
            self.send_message('parse error', message=string, reason='commands must contain args object')
        else:
            self.app.run(expr)

    def send_json(self, object):
        message = json.dumps(object)
        self.sendString(message)

    def send_message(self, type, **kwargs):
        message = {'type': type, 'args': kwargs}
        self.send_json(message)
