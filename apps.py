from collections import defaultdict
import traceback
from util import command, is_command
import re

def takes(**types):
    def inner(func):
        def func_wrapper(self, **kwargs):
            errors = []
            for i, j in kwargs.items():
                if i not in types:
                    errors.append("%s is an illegal parameter" % i)
                    continue
                if not isinstance(j, types[i]):
                    errors.append("%s should be a %s, (received %s)" %
                            (i, types[i], j.__class__.__name__))
                    continue
            for i in types:
                if i not in kwargs:
                    errors.append("%s expected but not received" % i)

            if errors:
                return {'type': 'bad arguments',
                        'args': {
                            'message': '\n'.join(errors)
                            }
                        }
            return func(self, **kwargs)
        return func_wrapper
    return inner


class App(object):
    def send_json(self, message):
        self.connection.send_json(message)

    def send_error(self, command, message, status='error'):
        error = {'args': {}}
        error['type'] = status
        error['args']['command'] = command
        error['args']['message'] = message
        self.connection.send_json(error)

    def __init__(self, connection):
        self.connection = connection

    def disconnect(self, reason):
        pass

    def get_command(self, command_name):
        return getattr(self, command_name, None)

    def run(self, command):
        try:
            command_name = command['type']
            args = command['args']
        except KeyError:
            self.send_error(command, 'was missing values')
            return
        function = self.get_command(command_name)
        if not function or not is_command(function):
            self.send_error(command,
                    "%s is not a valid command" % command_name,
                    'command not found')
            return
        try:
            result = function(**args)
        except:
            traceback.print_exc()
            self.send_error(command, traceback.format_exc())
            return
        if result != None:
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
    @takes(connection_type=basestring, username=basestring, password=basestring)
    def login(self, connection_type=str, username = '', password = ''):
        # TODO Actual login stuff
        self.connection.username = username
        try:
            self.connection.app = GameApp(self.connection, connection_type)
        except ImportError:
            return {'type': 'failure', 'args':
                    {'message': '%s is not a game type' % connection_type}}
        return {'type': 'success'}


class GameApp(App):
    games = defaultdict(dict)

    def __init__(self, connection, game_type):
        if '.' in game_type:
            raise ValueError("Game name cannot contain '.'")
        self.game_module = __import__('plugins.%s.game' % game_type,
                fromlist=['*'])
        App.__init__(self, connection)
        self.game_type = game_type
        self.game = None
        self.game_name = None

    @command
    def join_game(self, **game_details):
        # Check if game you want to join exists, otherwise create it.
        # If game exists, make certain you can join it
        # Transition to the GameApp state
        if 'game_name' in game_details:
            game_name = game_details['game_name']
        else:
            # If you don't specify a game number, find the lowest unused
            game_number = 1
            game_name = str(game_number)
            while game_name in self.games[self.game_type]:
                game_number += 1
                game_name = str(game_number)
            game_details['game_name'] = game_name
        if len(game_name) > 40:
            return {'type': 'failure', 'args': {'message': 'game name too long'}}
        if re.search('[/\\:*?"<>|@.\00]', game_name):
            return {'type': 'failure', 'args': {'message': 'game name contains illegal characters'}}
        if game_name in self.games[self.game_type]:
            # Join existing game
            self.game = self.games[self.game_type][game_name]
        else:
            # Create new game
            self.game = self.game_module.Game(game_details)
            self.games[self.game_type][game_name] = self.game
        # Attempt to connect to the game
        if self.game.state != 'new':
            self.game = None
            return {'type': 'failure', 'args': {'message': 'game has already started'}}
        else:
            self.game_name = game_name
            self.send_json({'type': 'success', 'args': {'name': game_name}})
            self.game.add_connection(self, game_details)
            return None

    @command
    def end_turn(self, **args):
        if not self.game or self.game.state != 'running':
            return {'type': 'failure',
                    'args': {'message': 'the game has not begun'}}
        if self.game.current_player._connection != self:
            return {'type': 'failure',
                    'args': {'message': 'not your turn'}}
        self.send_json({'type': 'success', 'args': {}})
        self.game.end_turn()
        return None


    @command
    def get_log(self, **args):
        if not self.game or self.game.state != 'over':
            return {'type': 'failure',
                    'args': {'message': 'the game has not begun'}}
        log = open(self.game.logger.path).read()
        return {'type': 'success', 'args':{
            'log': log}}

    def get_command(self, command_name):
        command = App.get_command(self, command_name)
        if command:
            return command
        if not self.game or self.game.state != 'running':
            return None

        def command(**args):
            if self.game.current_player._connection != self:
                return {'type': 'failure',
                        'args': {'message': 'not your turn'}}
            if 'actor' not in args:
                return {'type': 'bad arguments',
                        'args': {'message': 'actor required'}}
            actor = self.game.objects.get(args['actor'], None)
            del args['actor']
            if not actor:
                return {'type': 'bad arguments',
                        'args': {'message': 'actor does not exist'}}
            command = getattr(actor, command_name, None)
            if not command or not is_command(command):
                return {'type': 'error',
                        'args': {'message': '%s does not have command %s' %
                            (actor.__class__.__name__, command_name)}}
            #TODO make sure command is a command function rather than a security compromise
            value = command(**args)
            self.game.flush()
            if not value:
                return {'type': 'success', 'args': {}}
            else:
                return value
        command.is_command = True
        return command

    def disconnect(self, reason):
        if self.game:
            self.game.remove_connection(self)
            if not self.game.connections:
                del self.games[self.game_type][self.game_name]
            self.game = None
