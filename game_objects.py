from collections import defaultdict
import os
import json
from logger import Logger

#Future proof a bit
try:
    #Python 2
    from ConfigParser import SafeConfigParser as ConfigParser
except ImportError:
    #Python 3
    from configparser import ConfigParser

class GameObjectMeta(type):
    def __new__(meta, name, bases, dct):
        if '_name' not in dct:
            dct['_name'] = name.lower()
        if '_plural' not in dct:
            dct['_plural'] = dct['_name'] + 's'
        if '_relations' in dct:
            for key in dct['_relations']:
                @property
                def getter(self, key=key):
                    id = getattr(self, key+'_id')
                    return self.game.objects.get(id, None)
                @getter.setter
                def getter(self, value, key=key):
                    return setattr(self, key+'_id', value.id)
                dct[key] = getter
        if '_remotes' in dct:
            for key, source in dct['_remotes'].items():
                @property
                def getter(self, key=key, source=source):
                    return getattr(getattr(self, source), key)
                dct[key] = getter
        cls = type.__new__(meta, name, bases, dct)
        #record the type in its game
        cls._game._object_types[name] = cls
        return cls

class GameObject(object):
    # Root game object
    _game_state_attributes = set()

    def __init__(self, game, **attributes):
        #Bypass the __setattr__ method when setting the game
        object.__setattr__(self, 'game', game)
        self._new = True

        for key in self._game_state_attributes:
            setattr(self, key, None)
        #And the initial id, so id is defined
        object.__setattr__(self, 'id', game.next_id())

        game.add_object(self)
        self.removed = False
        for key, value in attributes.items():
            if key in self._game_state_attributes:
                setattr(self, key, value)

    def __setattr__(self, name, value):
        #We need to record changes for the game logs
        old = getattr(self, name, None)
        object.__setattr__(self, name, value)
        if self.game and \
                not self._new and \
                self.id in self.game.objects and \
                name in self._game_state_attributes and \
                old != value:
            self.game.changes[self.id][name] = value

    def jsonize(self):
        attributes = dict((key, getattr(self, key))
                          for key in self._game_state_attributes)
        attributes['id'] = self.id
        return attributes

    def remove(self):
        self.removed = True
        del self.game.objects[self.id]


    def before_turn(self):
        pass

    def after_turn(self):
        pass

class GameMeta(type):
    def __new__(meta, name, bases, dct):
        if '_relations' in dct:
            for key in dct['_relations']:
                @property
                def getter(self, key=key):
                    id = getattr(self, key+'_id')
                    return self.objects.get(id, None)
                @getter.setter
                def getter(self, value, key=key):
                    return setattr(self, key+'_id', value.id)
                dct[key] = getter
        cls = type.__new__(meta, name, bases, dct)
        cls._object_types = {}
        class Object(GameObject):
            _name = 'game_object'
            _game = cls
            #GameObject can't have the metaclass because it has no game
            __metaclass__ = GameObjectMeta
        cls.Object = Object
        return cls

class Game(object):
    _object_types = {}
    _globals = []
    __metaclass__ = GameMeta
    start_time = 10
    time_inc = 1
    # Shell game to show interaction
    def __init__(self, details):
        self.highest_id = -1
        self.additions = []
        self.changes = defaultdict(dict)
        self.global_changes = {}
        self.removals = []
        self.current_player = None

        self.objects = ObjectHolder(self)
        self.connections = []
        self.state = 'new'
        self.details = details
        self.game_name = details['game_name']
        self.logger = Logger(self)

        for i in self._globals:
            setattr(self, i, None)

    def add_object(self, object):
        self.additions.append(object)
        self.objects.add(object)

    def next_id(self):
        self.highest_id += 1
        return self.highest_id

    def send_all(self, message):
        for i in self.connections:
            i.connection.send_json(message)
        #TODO: Server-side glog
        self.logger.write(message)

    def flush(self):
        output = []

        for added in self.additions:
            output.append({'action':'add', 'values': added.jsonize(),
                'type': added.__class__.__name__})
            added._new = False

        for id, values in self.changes.items():
            output.append({'action': 'update', 'id': id, 'values': values})

        if self.global_changes:
            output.append({'action':'global_update',
                'values': self.global_changes})

        for removed in self.removals:
            output.append({'action': 'remove', 'id': removed.id})

        self.additions = []
        self.changes = defaultdict(dict)
        self.global_changes = {}
        self.removals = []

        if not output:
            return True

        message = {'type': 'changes',
                'args': {'changes': output}}

        self.send_all(message)

        return True

    def add_connection(self, connection, details):
        if self.state != 'new':
            return False
        self.connections.append(connection)
        if len(self.connections) == 2:
            self.start()
        return True

    def remove_connection(self, connection):
        if self.state == 'running':
            players = [i for i in self.players if i._connection is connection]
            if len(players) == 1:
                player = players[0]
                other = self.players[1 - player.id]
                self.end_game(other, 'disconnect')
        if connection in self.connections:
            self.connections.remove(connection)

    def start(self):
        self.state = 'running'
        for i in self.connections:
            Player = self._object_types['Player']
            player = Player(self, name = i.connection.username)
            player.time = self.start_time

            #Link the player to the connection, so we can easily associate them
            player._connection = i
            i.send_json({'type': 'player_id', 'args': {'id': player.id}})

        self.turn_number = -1
        self.before_start()
        self.flush()
        self.send_all({'type': 'start_game'})
        self.start_turn()

    def start_turn(self):
        self.turn_number += 1
        self.player_id = self.turn_number % 2
        self.current_player = self.players[self.player_id]
        self.current_player.time += self.time_inc
        self.before_turn()
        for i in self.objects.values():
            i.before_turn()
        self.flush()
        self.send_all({'type': 'start_turn'})

    def end_turn(self):
        self.send_all({'type': 'end_turn'})
        self.after_turn()
        for i in self.objects.values():
            i.after_turn()
        self.flush()

        winner, reason = self.check_winner()
        if winner:
            self.end_game(winner, reason)
        else:
            self.start_turn()

    def end_game(self, winner, reason):
        self.state = 'over'
        self.winner = winner.id
        self.send_all({'type': 'game_over', 'args': {'winner': winner.id, 'reason': reason}})
        self.objects.clear()
        self.logger.close()

    def __setattr__(self, key, value):
        object.__setattr__(self, key, value)
        if key in self._globals:
            self.global_changes[key] = value

    def load_config(self, name):
        def parse(value):
            try:
                return json.loads(value)
            except:
                return value
        if '.' not in name:
            name += '.cfg'
        path = os.path.join('plugins', self._name, 'config',  name)

        parser = ConfigParser()
        parser.optionxform = str
        parser.readfp(open(path))

        config = {key:parse(value) for key, value in parser.items('DEFAULT')}
        for s in parser.sections():
            config[s] = {key:parse(value) for key, value in parser.items(s)}
        return config


class ObjectHolder(dict):
    def __init__(self, game):
        dict.__init__(self)
        self.game = game
        for i in game._object_types.values():
            setattr(self.game, i._plural, [])

    def add(self, value):
        if not isinstance(value, self.game.Object):
            raise ValueError("Received object was not a game object")
        self[value.id] = value

    def clear(self):
        dict.clear(self)
        for i in self.game._object_types.values():
            setattr(self.game, i._plural, [])

    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        dict.__setitem__(self, key, value)
        for name, cls in self.game._object_types.items():
            if isinstance(value, cls):
                getattr(self.game, cls._plural).append(value)

    def __delitem__(self, key):
        value = self[key]
        dict.__delitem__(self, key)
        self.game.removals.append(value)
        for i in self.game._object_types.values():
            list = getattr(self.game, i._plural)
            if value in list:
                list.remove(value)
