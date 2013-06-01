from collections import defaultdict

class GameObjectMeta(type):
    def __new__(meta, name, bases, dct):
        cls = type.__new__(meta, name, bases, dct)
        cls._game.object_types[name] = cls
        return cls

class GameObject(object):
    # Root game object
    game_state_attributes = set()

    def __init__(self):
        self.id = self.game.next_id()
        self.game.additions.append(self)

    def __del__(self):
        self.game.remove(self)
        pass

    def __setattr__(self, name, value):
        if name in self.game_state_attributes:
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
    object_types = {}
    __metaclass__ = GameMeta
    # Shell game to show interaction
    def __init__(self):
        self.highest_id = 0
        self.additions = []
        self.changes = defaultdict(dict)
        self.deletions = []

    def add_object(self, object):
        self.additions.append(object)
