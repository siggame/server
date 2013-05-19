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
            output.append({'action': 'add', 'id': added.id, 'type':added.__class__.__name__})
        for id, changes in self.changes.items():
            output.append({'action': 'update', 'id': id, 'changes': changes})
        for deleted in self.deletions:
            output.append({'action': 'remove', 'id': deleted.id})

        self.additions = []
        self.changes = defaultdict(dict)
        self.deletions = []
        return output


class GameObject(object):
    # Root game object
    game_state_attributes = set()

    def __init__(self, game):
        self.game = game
        self.id = game.next_id()
        self.game.additions.append(self)
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

if __name__ == '__main__':
    # TODO: Separate tests out into their own part
    class XUnit(GameObject):
        # Example Unit that tracks the x attribute
        game_state_attributes = set(['x']) | GameObject.game_state_attributes

        def __init__(self, game, x):
            super(XUnit, self).__init__(game)
            self.x = x
            self.y = 'y'


    class YUnit(GameObject):
        # Example Unit that tracks the y attribute
        game_state_attributes = set(['y']) | GameObject.game_state_attributes

        def __init__(self, game, x):
            super(YUnit, self).__init__(game)
            self.x = x
            self.y = 'y'

    game = Game()
    g = GameObject(game)
    print g.game
    test = XUnit(game, 14)
    print "INITED", game.flush()
    test.x = 0
    test.y = 7
    print 'Writted', game.flush()

    other = YUnit(game, 14)
    print "INITED", game.flush()
    other.x = 0
    other.y = 7
    print 'Writted', game.flush()

    print test.jsonize()
    print other.jsonize()
