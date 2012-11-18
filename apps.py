def command(function):
    function.is_command = True

class App(object):
    commands = {}

    def __init__(self, connection):
        self.connection = connection

    def disconnect(self):
        pass

    def run(self, command):
        c = command['command']
        args = c['args']
        f = getattr(self, c)
        if not f or not getattr(f, 'is_command', False):
            pass

        return self.commands[c](self, **args)

class LoginApp(object):
    @command
    def login(self, username, password, type):
        pass
