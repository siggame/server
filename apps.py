from copy import copy
def command(function):
    function.is_command = True

class App(object):
    def send_error(self, command, message, status = 'error'):
        error = copy(command)
        error['status'] = status
        error['message'] = message
        self.connection.send_json(error)
    def __init__(self, connection):
        self.connection = connection

    def disconnect(self, reason):
        pass

    def run(self, command):
        try:
            c = command['command']
            args = command['args']
        except KeyError:
            self.send_error(command, 'was missing values')
            return
        f = getattr(self, c, None)
        if not f or not getattr(f, 'is_command', False):
            self.send_error(command, 'command not found')
            return

        return self.commands[c](self, **args)

class LoginApp(App):
    """
    This is the starting app for connections.
    This facilitates any authentication we want to do
    and let's them specify what kind of connection they want.

    This should detect all the game plugins and expose them.
    Also, the arena app, and any others we think of later.
    """

    @command
    def login(self, username, password, type):
        pass
