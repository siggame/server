from heapq import heappop, heappush

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

class PathFinder():

    def h_score(self, current, dest):
        return self.distance(current[0], current[1], dest[0], dest[1])

    def get_adjacent(self, source):
        return []

    def find_path(self,  source, dest):
        closed = {source: None}
        if source == dest:
            return [source]
         # 0 = f, 1 = current (x,y), 2 = g
        open = [ (self.h_score(source, dest), source, 0) ]
        while len(open) > 0:
            h, point, g = heappop(open)
            for neighbor in self.get_adjacent(point):
                if neighbor in closed:
                    continue
                closed[neighbor] = point
                if neighbor == dest:
                    return self.make_path(closed, dest)
                heappush(open, (g+1+self.hscore(neighbor, dest),
                    neighbor, g+1) )
        return None

    def make_path(self, closed, dest):
        current = dest
        path = [current]
        while closed[current]:
            current = closed[current]
            path.append(current)

        return reversed(path)

    def distance(self, x1, y1, x2, y2):
        return abs(x2-x1) + abs(y2-y1)



