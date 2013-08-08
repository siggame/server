import os
import errno
import json

class Logger(object):
    def __init__(self, game):
        self.game = game
        self.directory = os.path.join('logs', game._name)
        self.path = os.path.join(self.directory, game._game_name + '.glog')
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
        self.write({'type': 'version', 'args': {'game': self.game._game_version,
            'server': self.game._server_version
            }})

    def write(self, data):
        message = json.dumps(data)
        self.file.write(message)
        self.file.write('\n')

    def close(self):
        self.file.close()
