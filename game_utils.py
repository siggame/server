import random
from functools import wraps

from os import listdir
from os.path import isfile, join
from math import ceil

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

class TileMapGenerator(object):
    class Point(object):
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.value = ' '

    def __init__(self, game, width=20, height=20):
        self.game = game
        self.width = width
        self.height = height
        self.grid = {}
        self.init_grid()
        self.load_tiles()

    def generate(self):
        self.lay_tiles()

    def init_grid(self):
        for i in range(self.width):
            for j in range(self.height):
                self.grid[i, j] = self.Point(i, j)


    def load_tiles(self):
        #TODO: Load tiles
        directory = join('plugins', self.game._name, 'config', 'tiles')
        files = [ f for f in listdir(directory) if isfile(join(directory,f)) ]
        self.tiles = []
        for f in files:
            map = open(join(directory, f)).readlines()
            map = [[j  for j in i[:len(map)]] for i in map]
            self.tiles.append(map)

    def lay_tiles(self):
        #super deep loop go!
        tile_size = len(self.tiles[0])
        width = int(ceil(self.width / tile_size / 2))
        height = int(ceil(self.height / tile_size))
        for i in range(width):
            for j in range(height):
                t = random.choice(self.tiles)
                #transform the tile for variety
                #transpose
                if random.randint(0, 1):
                    t = map(list, zip(*t))
                #flip columns
                if random.randint(0, 1):
                    t = reversed(t)
                flip_rows = random.randint(0, 1)
                for k, row in enumerate(t):
                    #flip rows
                    if flip_rows:
                        row = reversed(row)
                    for l, col in enumerate(row):
                        x = i * tile_size + k
                        y = j * tile_size + l
                        tile = self.grid[x, y]
                        other_tile = self.grid[self.width - x - 1, y]
                        tile.value = other_tile.value = col

    def connect_map(self, connect = ' '):
        while True:
            tiles = [i for i in self.grid.values() if i.value in connect]
            tile = random.choice(tiles)
            c = self._find_connected(tile, connect)
            if len(c) == len(tiles):
                return
            walls = [i for i in self.grid.values() if i.value not in connect]
            wall = random.choice(walls)
            other_wall = self.grid[self.width - wall.x - 1, wall.y]
            wall.value = other_wall.value =connect[0]

    def _find_connected(self, tile, connect):
        open = [(tile.x, tile.y)]
        connected = set()
        while open:
            t = open.pop()
            x, y = t
            for i, j in [ (x-1, y), (x+1, y), (x, y-1), (x, y+1)]:
                if 0 <= i < self.width and 0 <= j < self.height:
                    tile = self.grid[i, j]
                    if (i, j) not in connected and tile.value in connect:
                        connected.add((i, j))
                        open.append((i, j))
        return connected

    def sprinkle(self, num, value, onto=' ', max_x = None):
        for i in range(num):
            tiles = [i for i in self.grid.values() if i.value in onto]
            if max_x is not None:
                tiles = [i for i in tiles if i.x <= max_x]
            if not tiles:
                return
            tile = random.choice(tiles)
            other_tile = self.grid[self.width - tile.x - 1, tile.y]
            tile.value = other_tile.value = value

    def __repr__(self):
        print self.width, self.height
        val = ''
        for y in range(self.height):
            for x in range(self.width):
                val += self.grid[x, y].value
            val += '\n'
        return val

    def __iter__(self):
        for y in range(self.height):
            for x in range(self.width):
                yield self.grid[x, y]

def takes(**types):
    def inner(func):
        @wraps(func)
        def func_wrapper(self, **kwargs):
            errors = []
            for i, j in kwargs.items():
                if i not in types:
                    errors.append("%s is an illegal parameter" % i)
                    continue
                if callable(types[i]):
                    try:
                        j = types[i](j)
                        kwargs[i] = j
                    except ValueError:
                        errors.append("%s should be a %s, (received %s)" %
                                (i, types[i].__name__, j.__class__.__name__))
                elif isinstance(types[i], basestring):
                    if types[i] not in self.game._object_types:
                        print("{} for argument {} of {} not found in game types".
                                format(types[i], i, func.__name__))
                        continue
                    if j not in self.game.objects:
                        errors.append("object {} for {} does not exist".format(j, i))
                        continue
                    j = self.game.objects[j]
                    if not isinstance(j, types[i]):
                        errors.append("object {} for {} does is not {}".
                                format(j, i, types[i]))
            for i in types:
                if i not in kwargs:
                    errors.append("%s expected but not received" % i)

            if errors:
                return {'type': 'failure',
                        'args': {
                            'message': '\n'.join(errors)
                            }
                        }
            return func(self, **kwargs)
        return func_wrapper
    return inner

def success(**args):
    return {'type': 'success', 'args': args}

def failure(**args):
    return {'type': 'failure', 'args': args}
