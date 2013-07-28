from collections import defaultdict

class GameObjectMeta(type):
    def __new__(meta, name, bases, dct):
        cls = type.__new__(meta, name, bases, dct)
        #record the type in its game
        cls._game._object_types[name] = cls
        return cls

class GameObject(object):
    # Root game object
    game_state_attributes = set()

    def __init__(self, game, **attributes):
        #Bypass the __setattr__ method when setting the game
        object.__setattr__(self, 'game', game)
        #And the initial id, so id is defined
        object.__setattr__(self, 'id', game.next_id())

        for key in self.game_state_attributes:
            setattr(self, key, None)
        game.add_object(self)
        for key, value in attributes.items():
            if key in self.game_state_attributes:
                setattr(self, key, value)

    def __setattr__(self, name, value):
        #We need to record changes for the game logs
        object.__setattr__(self, name, value)
        if self.game and \
                self.id in self.game.objects and \
                name in self.game_state_attributes:
            self.game.changes[self.id][name] = value

    def jsonize(self):
        attributes = dict((key, getattr(self, key))
                          for key in self.game_state_attributes)
        attributes['id'] = self.id
        return attributes

class GameMeta(type):
    def __new__(meta, name, bases, dct):
        cls = type.__new__(meta, name, bases, dct)
        cls._object_types = {}
        class Object(GameObject):
            _game = cls
            #GameObject can't have the metaclass because it has no game
            __metaclass__ = GameObjectMeta
        cls.Object = Object
        return cls

class Game(object):
    _object_types = {}
    _globals = []
    __metaclass__ = GameMeta
    # Shell game to show interaction
    def __init__(self):
        self.highest_id = 0
        self.additions = []
        self.changes = defaultdict(dict)
        self.global_changes = {}
        self.deletions = []

        self.globals = Globals(self)
        self.objects = ObjectHolder(self)
        self._connections = []
        self.state = 'new'

    def add_object(self, object):
        self.additions.append(object)
        self.objects.add(object)

    def next_id(self):
        self.highest_id += 1
        return self.highest_id

    def flush(self):
        #TODO: Clear list of changes and send them all to the players
        pass

    def add_connection(self, connection, details):
        if self.state != 'new':
            return False
        self.connections.append(connection)
        if len(self.connections) == 2:
            self.start()
        return True

    def start(self):
        #TODO: initialize the game
        pass


class ObjectHolder(dict):
    def __init__(self, game):
        dict.__init__(self)
        self._game = game
        for i in game._object_types:
            setattr(self, i, [])

    def add(self, value):
        if not isinstance(value, self._game.Object):
            raise ValueError("Received object was not a game object")
        self[value.id] = value

    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        dict.__setitem__(self, key, value)
        for name, cls in self._game._object_types.items():
            if isinstance(value, cls):
                getattr(self, name).append(value)

    def __delitem__(self, key):
        value = self[key]
        dict.__delitem__(self, key)
        for name in self._game._object_types:
            list = getattr(self, name)
            if value in list:
                list.remove(value)

class Globals(dict):
    def __init__(self, game):
        dict.__init__(self)
        self._game = game
        for i in game._globals:
            dict.__setitem__(i, None)

    def __setitem__(self, key, value):
        if key not in self._game._globals:
            raise ValueError("%s is not a known global" % key)
        dict.__setitem__(self, key, value)
        self._game.global_changes[key] = value

    def __delitem__(self, key):
        #we don't want globals to drop out of existence
        self[key] = None
