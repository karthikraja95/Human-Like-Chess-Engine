import chess
import chess.uci
import chess.pgn

import pytz

import random
import json
import os
import os.path
import time
import datetime

tz = pytz.timezone('Canada/Eastern')

_stockfishPath = 'stockfish'
_lc0Path = 'lc0'

_movetime = 10

networksDir = '/u/reidmcy/w/chess/imitation-chess/networks'

stockfish_SKILL = [0, 3, 6, 10, 14, 16, 18, 20]
stockfish_MOVETIMES = [50, 100, 150, 200, 300, 400, 500, 1000]
stockfish_DEPTHS = [1, 1, 2, 3, 5, 8, 13, 22]

class TourneyEngine(object):
    def __init__(self, engine, name, movetime = None, nodes = None, depth = None):
        self.engine = engine
        self.name = f"{type(self).__name__} {name}"
        self.movetime = movetime
        self.depth = depth
        self.nodes = nodes

    def __repr__(self):
        return f"<{self.name}>"

    def __str__(self):
        return self.name

    def newgame(self):
        self.engine.ucinewgame()

    def getMove(self, board):
        self.engine.position(board)
        moves = self.engine.go(movetime = self.movetime, nodes = self.nodes, depth = self.depth)
        return moves.bestmove

    def __del__(self):
        try:
            self.engine.quit()
        except chess.engine.EngineTerminatedException:
            pass
        except ValueError:
            pass

class _MoveHolder(object):
    def __init__(self, move):
        self.bestmove = move


class _RandomEngineBackend(object):
    def __init__(self):
        self.nextMove = None

    def position(self, board):
        self.nextMove = random.choice(list(board.legal_moves))

    def go(self, **kwargs):
        return _MoveHolder(self.nextMove)

    def quit(self):
        pass

    def ucinewgame(self):
        pass

class RandomEngine(TourneyEngine):
    def __init__(self, engine = None, name = 'random', movetime = None, nodes = None, depth = None):
        super().__init__(_RandomEngineBackend(), name, movetime = movetime, nodes = nodes)

class StockfishEngine(TourneyEngine):
    def __init__(self, skill = 20, movetime = _movetime, depth = 30, sfPath = _stockfishPath):
        self.skill = skill

        self.stockfishPath = sfPath

        engine = chess.uci.popen_engine([self.stockfishPath])

        engine.setoption({'skill' : skill, 'Ponder' : 'false', 'UCI_AnalyseMode' : 'false'})

        super().__init__(engine, f's{skill} d{depth} {movetime}', movetime = movetime, depth = depth)

class LC0Engine(TourneyEngine):
    def __init__(self, weightsPath = None, nodes = None, movetime = _movetime, isHai = True, lc0Path = _lc0Path, threads = 1):
        self.weightsPath = weightsPath
        self.lc0Path = lc0Path
        self.isHai = isHai
        self.threads = threads
        engine = chess.uci.popen_engine([self.lc0Path, f'--weights={weightsPath}', f'--threads={threads}'])

        super().__init__(engine, f"{os.path.basename(self.weightsPath)[:-6]} {movetime}", movetime = movetime, nodes = nodes)

class HaibridEngine(LC0Engine):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, isHai = True)

class LeelaEngine(LC0Engine):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, isHai = False)

def playGame(E1, E2, round = None):

    timeStarted = datetime.datetime.now(tz)
    board = chess.Board()

    E1.newgame()
    E2.newgame()

    players = [E1, E2]
    i = 0
    while not board.is_game_over():
        E = players[i % 2]
        board.push(E.getMove(board))
        i += 1
    pgnGame = chess.pgn.Game.from_board(board)

    pgnGame.headers['Event'] = f"{E1.name} vs {E2.name}"
    pgnGame.headers['White'] = E1.name
    pgnGame.headers['Black'] = E2.name
    pgnGame.headers['Date'] = timeStarted.strftime("%Y-%m-%d %H:%M:%S")
    if round is not None:
        pgnGame.headers['Round'] = round
    return pgnGame

def playTourney(E1str, E2str, num_rounds, resultsDir):
    tstart = time.time()
    E1 = stringToEngine(E1str)

    E2 = stringToEngine(E2str)

    games = []
    i = 0
    while i < num_rounds:
        print(f"Starting round {i} {E1.name} vs {E2.name}", flush = True)
        try:
            if i % 2 == 0:
                players = [E1, E2]
            else:
                players = [E2, E1]
            pgnGame = playGame(*players, round = i + 1)
        except BrokenPipeError:
            print("BrokenPipe: {E1.name} v {E2.name}")
            E1 = stringToEngine(E1str)
            E2 = stringToEngine(E2str)
            continue
        else:
            pgnStr = str(pgnGame)

            e1Name = json.loads(E1str)['name']
            e2Name = json.loads(E2str)['name']
            with open(os.path.join(resultsDir, f"{e1Name}-{e2Name}.pgn"), 'a') as f:
                for game in games:
                    f.write(pgnStr)
                    f.write('\n\n')

            games.append(pgnStr)
            i += 1
    print(f"Done {num_rounds} games in {time.time() - tstart : .2f}s of {E1.name} vs {E2.name}")

    return games

def listRandoms():
    return [json.dumps({'engine' : 'random', 'config' : {}, 'name' : 'random'})]

def listLeelas(configs = None):
    if configs is None:
        configs = {}
    vals = []
    for e in os.scandir(os.path.join(networksDir, 'leela_weights')):
        if e.name.endswith('pb.gz'):
            v = {'weightsPath' : e.path}
            v.update(configs)
            vals.append(v)
    return [json.dumps({'engine' : 'leela', 'config' : v, 'name' : f"leela_{os.path.basename(v['weightsPath']).split('-')[1]}"}) for v in vals]

def listHaibrids(configs = None):
    if configs is None:
        configs = {}
    vals = []
    for e in os.scandir(os.path.join(networksDir)):
        if e.name.endswith('-64x6-140000.pb.gz'):
            v = {'weightsPath' : e.path}
            v.update(configs)
            vals.append(v)
    return [json.dumps({'engine' : 'hiabrid', 'config' : v, 'name' : f"hiabrid_{os.path.basename(v['weightsPath']).split('-')[0]}"}) for v in vals]

def fileNameToEngineName(s):
    if 'stockfish' in s:
        n, s, m, d = s.split('_')
        return "StockfishEngine s{} d{} {}".format(s[:-1], d[:-1], m[:-1])
    elif 'leela' in s:
        n, e = s.split('_')
        return "LeelaEngine t3-{}".format(e)
    elif 'hiabrid' in s:
        n, e = s.split('_')
        return "HaibridEngine {}-64x6-140000".format(e)
    elif 'random' in s:
        return 'RandomEngine random'
    raise RuntimeError(f"{s} is not a valid engine file name")

def listStockfishs():
    vals = []
    for s, m, d in zip(stockfish_SKILL, stockfish_MOVETIMES, stockfish_DEPTHS):
        vals.append({
            'skill' : s,
            'movetime' : m,
            'depth' : d,
        })
    return [json.dumps({'engine' : 'stockfish', 'config' : v, 'name' : f"stockfish_{v['skill']}s_{v['movetime']}m_{v['depth']}d"}) for v in vals]

def stringToEngine(s):
    dat = json.loads(s)
    if dat['engine'] == 'stockfish':
        return StockfishEngine(**dat['config'])
    elif dat['engine'] == 'hiabrid':
        return HaibridEngine(**dat['config'])
    elif dat['engine'] == 'leela':
        return LeelaEngine(**dat['config'])
    elif dat['engine'] == 'random':
        return RandomEngine(**dat['config'])
    else:
        raise RuntimeError(f"Invalid config: {s}")

def playStockfishGauntlet(E, num_rounds):
    pgns = []
    for config in listStockfishs():
        SF = StockfishEngine(**config)
        p = playTourney(E, SF)
        pgns += p
    return pgns

def listAllEngines(hiabridConfig = None, leelaConfig = None):
    return listHaibrids(configs = hiabridConfig) + listLeelas(configs = leelaConfig) + listStockfishs() + listRandoms()
