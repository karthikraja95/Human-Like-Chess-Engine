import imitation_chess
import chess

import bz2
import os
import gc
import sys
import re

moveRegex = re.compile(r'\d+[.] (\S+) (?:{[^}]*} )?(\S+)')

maxMoves = 50

outputPath = '/datadrive/holdout/'

#outputPath = '.'

class LightGamesFile(object):
    def __init__(self, path):
        self.f = bz2.open(path, 'rt')

    def __iter__(self):
        while True:
            g = chess.pgn.read_game(self.f)
            if g is None:
                raise StopIteration
            yield g

    def __del__(self):
        try:
            self.f.close()
        except AttributeError:
            pass

    def readNextGame(self):
        self.f.readline()
        ret = {}
        for l in self.f:
            if len(l) < 2:
                if len(ret) == 3:
                    break
                else:
                    raise RuntimeError
            elif len(ret) == 3:
                pass
            elif l.startswith('[Site'):
                ret['Site'] = l.split('/')[-1][:-3]
            elif l.startswith('[WhiteElo'):
                ret['WhiteElo'] = l[11:-3]
            elif l.startswith('[BlackElo'):
                ret['BlackElo'] = l[11:-3]
        ret['moves'] = re.findall(moveRegex, self.f.readline())
        return ret

def getBoardMoveMap(moveDat, maxNumMoves = None):
    d = {}
    board = chess.Board()
    for mw, mb in moveDat[:maxNumMoves // 2]:
        try:
            for m in [mw, mb]:
                mFen = board.fen()
                board.push_san(m)
                d[mFen] = m
        except ValueError:
            break
    return d

def fenFile(path):
    inputName = os.path.basename(path)[:-8]
    outputName = os.path.join(outputPath, f"mapping_{inputName}.csv")
    print("Loading: ", path)
    print("To: ", outputName)

    games = LightGamesFile(path)

    with open(outputName, 'w') as f:
        f.write("board,move,game,BlackElo,WhiteElo\n")
        i = 0
        while True:
            try:
                gDat = games.readNextGame()
            except RuntimeError:
                break
            d = getBoardMoveMap(gDat['moves'], maxNumMoves = maxMoves)
            try:
                gameID = gDat['Site']
                BlackElo = gDat['BlackElo']
                WhiteElo = gDat['WhiteElo']
            except KeyError as e:
                print()
                print(e)
                continue
            for k, v in d.items():
                f.write(f"{k},{v},{gameID},{BlackElo},{WhiteElo}\n")
            i += 1
            if i % 1000 == 0:
                print(f"{i}: {gameID}")
                f.flush()

    print("Done: ", path)

def main():
    for gamesPath in sys.argv[1:]:
        fenFile(gamesPath)

if __name__ == '__main__':
    main()
