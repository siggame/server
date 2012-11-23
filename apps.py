from copy import copy
from collections import defaultdict


def command(function):
    function.is_command = True
    return function


class App(object):
    def send_error(self, command, message, status='error'):
        error = copy(command)
        error['status'] = status
        error['message'] = message
        self.connection.send_json(error)

    def __init__(self, connection):
        self.connection = connection

    def disconnect(self, reason):
        pass

    def get_command(self, command_name):
        return getattr(self, command_name, None)

    def run(self, command):
        try:
            command_name = command['command']
            args = command['args']
        except KeyError:
            self.send_error(command, 'was missing values')
            return
        function = self.get_command(command_name)
        if not function or not getattr(function, 'is_command', False):
            self.send_error(command, 'command not found')
            return
        try:
            result = function(**args)
        except TypeError:
            self.send_error(command, "incorrect arguments")
            return
        self.connection.send_json(result)


class LoginApp(App):
    """
    This is the starting app for connections.
    This facilitates any authentication we want to do
    and let's them specify what kind of connection they want.

    This should detect all the game plugins and expose them.
    Also, the arena app, and any others we think of later.
    """

    @command
    def login(self, username, password, connection_type):
        # TODO Actual login stuff
        self.connection.app = GameApp(self.connection)


class GameApp(App):
    games = defaultdict(dict)

    @command
    def join_game(self, game_type, **game_details):
        # Check if game you want to join exists, otherwise create it.
        # If game exists, make certain you can join it
        # Transition to the GameApp state
        # TODO Sanitize game_type
        if 'game_number' in game_details:
            game_number = game_details['game_number']
        else:
            # If you don't specify a game number, find the lowest unused
            game_number = 1
            while game_number in self.games[game_type]:
                game_number += 1
        if game_number in self.games[game_type]:
            # Join existing game
            self.game = self.games[game_type][game_number]
        else:
            # Create new game
            try:
                game_module = __import__('plugins.%s.game' % game_type,
                                         fromlist=['*'])
            except ImportError:
                #TODO Send some error
                return
            self.game = game_module.Game(game_details)
            self.games[game_type][game_number] = self.game
        # Attempt to connect to the game
        if self.game.add_connection(self, game_details):
            # Monkey patch so all future commands deal directly with the game
            self.get_command = self.get_command_from_game
        #TODO Make certain game objects are removed from self.games when they
        #TODO end.  Also, its more minor but game_type's should be removed as
        #TODO well.

    def get_command_from_game(self, command_name):
        return getattr(self.game, command_name, None)
