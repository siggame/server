import apps
from twisted.internet import reactor

DELAY=.1

def tick():
    for game_type in apps.GameApp.games.values():
        for game in game_type.values():
            if game.state == 'running':
                player = game.current_player
                player.time -= DELAY
                if player.time < 0:
                    other = game.players[1 - game.player_id]
                    game.end_game(other, 'time')

    reactor.callLater(DELAY, tick)

def install():
    reactor.callWhenRunning(reactor.callLater, DELAY, tick)
