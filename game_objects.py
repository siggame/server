from collections import defaultdict

class GameObjectMeta(type):
    def __new__(meta, name, bases, dct):
        cls = type.__new__(meta, name, bases, dct)
        cls._game._object_types[name] = cls
        return cls

class GameObject(object):
    # Root game object
    game_state_attributes = set()

    def __init__(self, game, **attributes):
        for key in self.game_state_attributes:
            setattr(self, key, None)
        self.game = game
        self.id = game.next_id()
        game.add(self)
        for key, value in attributes:
            if key in self.game_state_attributes:
                setattr(self, key, value)

    def __del__(self):
        self.game.remove(self)

    def __setattr__(self, name, value):
        if self.game and name in self.game_state_attributes:
            self.game.changes[self.id][name] = value
        object.__setattr__(self, name, value)

    def jsonize(self):
        attributes = dict((key, getattr(self, key))
                          for key in self.game_state_attributes)
        attributes['id'] = self.id
        return attributes

class GameMeta(type):
    def __new__(meta, name, bases, dct):
        cls = type.__new__(meta, name, bases, dct)
        class Object(GameObject):
            _game = cls
            __metaclass__ = GameObjectMeta
        cls.Object = Object
        return cls

class Game(object):
    _object_types = {}
    _globals = []
    __metaclass__ = GameMeta
    # Shell game to show interaction
    def __init__(self):
        self.globals = Globals(self)
        for i in self._globals:
            self.globals[i] = None
        self.objects = ObjectHolder(self)
        self.highest_id = 0
        self.additions = []
        self.changes = defaultdict(dict)
        self.global_changes = {}
        self.deletions = []

    def add_object(self, object):
        self.add.append(object)

class ObjectHolder(dict):
    def __init__(self, game):
        dict.__init__(self)
        self._game = game
        for i in game._object_types:
            setattr(self, i, [])

    def add(self, value):
        if not isinstance(value, self.game.Object):
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
        self[key] = None
