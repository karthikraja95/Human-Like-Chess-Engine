import re
import sys
import os
import os.path


outputSuffix = '-clean'

def getNextGame(f):
    out = ''
    isBullet = False
    ncount = 0
    for l in f:
        out += l
        if l == '\n':
            ncount += 1
            if ncount > 1:
                break
        elif l.startswith('[Event '):
            if 'bullet' in l.lower():
                isBullet = True
    return out, isBullet

def cleanPGN(targetPath):
    dirname, filename = os.path.split(os.path.splitext(targetPath)[0])
    outputName = os.path.join(dirname, f"{filename}{outputSuffix}.pgn")
    eloDir = os.path.basename(os.path.abspath(dirname))
    with open(targetPath) as fin, open(outputName, 'w') as fout:
        i = 0
        removed = 0
        while True:
            game, isBul = getNextGame(fin)
            if len(game) < 1:
                break
            elif not isBul:
                fout.write(game)
            else:
                removed += 1
            i += 1
            if i % 10000 == 0:
                print(f"{eloDir}\t{str(i).ljust(8)}\tratio: {(i - removed) / i:.2f}", end = '\r')
    print(f"{eloDir}\t{filename}.pgn to {filename}{outputSuffix}.pgn: ratio {(i - removed )/ i:.2f} for {i}")
    os.remove(targetPath)

def main():
    for gamesPath in sys.argv[1:]:
        cleanPGN(gamesPath)

if __name__ == '__main__':
    main()
