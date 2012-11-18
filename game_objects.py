import json
from collections import defaultdict


class Game(object):
    # Shell game to show interaction
    def __init__(self):
        self.highest_id = 0
        self.additions = []
        self.changes = defaultdict(dict)
        self.deletions = []

    def next_id(self):
        self.highest_id += 1
        return self.highest_id

    def flush(self):
        output = []
        for added in self.additions:
            output.append({'action': 'add', 'id': added})
        for id, changes in self.changes.items():
            output.append({'action': 'update', 'id': id, 'changes': changes})
        for deleted in self.deletions:
            output.append({'action': 'remove', 'id': deleted})

        self.additions = []
        self.changes = defaultdict(dict)
        self.deletions = []
        return output


class Game_Object(object):
    # Root game object
    game_state_attributes = set()

    def __init__(self, game):
        self.game = game
        self.id = game.next_id()
        # TODO Register self with game objects stuff, which also handles animation

    def __del__(self):
        # TODO Unregister self with game objects stuff, which also handles animation
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


class X_Unit(Game_Object):
    # Example Unit that tracks the x attribute
    game_state_attributes = set(['x']) | Game_Object.game_state_attributes

    def __init__(self, game, x):
        super(X_Unit, self).__init__(game)
        self.x = x
        self.y = 'y'


class Y_Unit(Game_Object):
    # Example Unit that tracks the y attribute
    game_state_attributes = set(['y']) | Game_Object.game_state_attributes

    def __init__(self, game, x):
        super(Y_Unit, self).__init__(game)
        self.x = x
        self.y = 'y'

game = Game()
g = Game_Object(game)
print g.game
test = X_Unit(game, 14)
print "INITED", game.flush()
test.x = 0
test.y = 7
print 'Writted', game.flush()

other = Y_Unit(game, 14)
print "INITED", game.flush()
other.x = 0
other.y = 7
print 'Writted', game.flush()

print test.jsonize()
print other.jsonize()
