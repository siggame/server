import os
import errno
import json
import time

class Logger(object):
    def __init__(self, game):
        self.game = game
        self.directory = os.path.join('logs', game._name)
        self.path = os.path.join(self.directory, game.game_name + '.glog')
        try:
            os.makedirs(self.directory)
        except OSError as exception:
            #Don't care if the directory already exists
            if exception.errno != errno.EEXIST:
                raise
        #TODO: Make this file compressed
        self.file = open(self.path, 'w')
        self.start_file()

    def start_file(self):
        self.file.write('[')
        data = {'type': 'metadata', 'args': {'game_version': self.game._game_version,
            'server_version': self.game._server_version,
            'id': self.game.game_name,
            'timestamp': int(time.time())
            }}
        message = json.dumps(data)
        self.file.write(message)


    def write(self, data):
        message = json.dumps(data)
        self.file.write(',\n')
        self.file.write(message)

    def close(self):
        self.file.write(']')
        self.file.close()
