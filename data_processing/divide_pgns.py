import imitation_chess
import chess

import bz2
import os
import gc
import sys

outputPath = '/datadrive/split_games/'

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

def writePGNdict(pgnDict, outputDir):
    #print("Writing: ", end = '')
    for i, v in pgnDict.items():
        #print(i, end = ' ')
        with open(os.path.join(outputDir, "{:.0f}00.pgn".format(i).rjust(4,'0')), 'a') as f:
            f.write('\n\n'.join(v))
            f.write('\n\n')
    print()

def writeGameELOs(games, outputDir):

    os.makedirs(outputDir, exist_ok = False)

    sortedPGNs = {}
    for i, g in enumerate(games):
        try:
            BlackElo = round(int(g.headers['BlackElo']) + 49, -2)
            WhiteElo = round(int(g.headers['WhiteElo']) + 49, -2)
        except ValueError:
            continue
        if BlackElo == WhiteElo and g.headers['Result'] != '*':
            try:
                sortedPGNs[BlackElo].append(str(g))
            except KeyError:
                sortedPGNs[BlackElo] = [str(g)]

        if i % 1000 == 0:
            print("Processed {} games".format(i), end = '\r')
        if i % 10000 == 0 and i > 1:
            writePGNdict(sortedPGNs, outputDir)
            sortedPGNs.clear()

    writePGNdict(sortedPGNs, outputDir)
    print()

def processPath(path):
    outputDirName = os.path.basename(path)[:-8]
    outputDir = os.path.join(outputPath, outputDirName)

    print("Loading: ", path)
    print("To: ", outputDir)

    games = LightGamesFile(path)
    gameElos = writeGameELOs(games, outputDir)
    print("Done: ", path)

def main():

    for gamesPath in sys.argv[1:]:
        try:
            processPath(gamesPath)
        except FileExistsError:
            print("Skipping: ", gamesPath)

if __name__ == '__main__':
    main()
