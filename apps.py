from copy import copy
def command(function):
    function.is_command = True

class App(object):
    commands = {}

    def __init__(self, connection):
        self.connection = connection

    def disconnect(self, reason):
        pass

    def run(self, command):
        c = command['command']
        args = command['args']
        f = getattr(self, c, None)
        if not f or not getattr(f, 'is_command', False):
            error = copy(command)
            error['status'] = 'error'
            error['message'] = 'command not found'
            self.connection.send_json(error)
            return

        return self.commands[c](self, **args)

class LoginApp(App):
    @command
    def login(self, username, password, type):
        pass
