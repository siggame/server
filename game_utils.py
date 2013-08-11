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

    def f_score(self, h, g):
        return self.h_score(h[0], h[1]) + self.g_score(g[0], g[1])

    def g_score(self, source, current):
        return self.distance(source[0], source[1], current[0], current[1])

    def h_score(self, current, dest):
        return self.distance(current[0], current[1], dest[0], dest[1])

    def getAdjacent(self, source):
        pass

    def pathFind(self,  sourceX, sourceY, destX, destY):
        closedSet = set()
        closedTup = set()
         # 0 = h, 1 = current (x,y), 2 = parent (x,y) 3 = g
        open = [(self.h_score((sourceX, sourceY), (destX, destY)), (sourceX, sourceY), None, 0)]
        openTup = [(sourceX, sourceY)]
        path = []
        while len(open) > 0:
            current = heappop(open)
            if current[1] == (destX, destY):
                return self.makePath()
            closedSet.add(current)
            closedTup.add(current[1])
            openTup.remove(current[1])
            open.remove(current)
            for neighbor in self.getAdjacent((current[1][0], current[1][1])):
                if neighbor in closedSet:
                  continue
                g = current[3] + self.distance(current[1][0], current[1][1], neighbor[0], neighbor[1])
                if neighbor == (destX, destY) or self.distance(neighbor[0], neighbor[1], sourceX, sourceY) <= g+1 and neighbor not in openTup:
                  pass

    def goTo(self, sourceX, sourceY, destX, destY):
        pass

    def makePath(self):
        pass

    def distance(self, x1, y1, x2, y2):
        return abs(x2-x1) + abs(y2-y1)



