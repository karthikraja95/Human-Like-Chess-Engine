import bz2
import collections.abc



import chess.pgn

class GamesFile(collections.abc.Iterable):
    def __init__(self, path, cacheGames = False):
        self.path = path
        self.f = bz2.open(self.path, 'rt')

        self.cache = cacheGames
        self.games = []

    def __iter__(self):
        for g in self.games:
            yield g
        while True:
            yield self.loadNextGame()

    def loadNextGame(self):
        g = chess.pgn.read_game(self.f)
        if g is None:
            raise StopIteration
        if self.cache:
            self.games.append(g)
        return g

    def __getitem__(self, val):
        if isinstance(val, slice):
            return [self[i] for i in range(*val.indices(10**20))]
        elif isinstance(val, int):
            if len(self.games) < val:
                return self.games[val]
            elif val < 0:
                raise IndexError("negative indexing is not supported") from None
            else:
                g = self.loadNextGame()
                for i in range(val - len(self.games)):
                    g = self.loadNextGame()
                return g
        else:
            raise IndexError("{} is not a valid input".format(val)) from None

    def __del__(self):
        try:
            self.f.close()
        except AttributeError:
            pass

def getBoardMoveMap(game, maxMoves = None):
    d = {}
    board = game.board()
    for i, move in enumerate(game.main_line()):
        d[board.fen()] = move.uci()
        board.push(move)
        if maxMoves is not None and i > maxMoves:
            break
    return d
