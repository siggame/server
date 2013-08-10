class Grid(object):
    def __init__(self, game, type, dimensions = ('x', 'y')):
        self.game = game
        self.type = type
        self.grid = {}
        self.dimensions = dimensions

    def generate(self, x, y):
        for i in range(x):
            for j in range(y):
                values = {self.dimensions[0]: i,
                        self.dimensions[1]: j}
                self.grid[i, j] = self.type(self.game, **values)

    def populate(self):
        objects = getattr(self.game, self.type._plural)
        for i in objects:
            coordinate = tuple(getattr(i, key) for key in self.dimensions)
            self.grid[coordinate] = i

    def __getitem__(self, key):
        return self.grid.get(key, None)
