import re
import sys
import os
import os.path
import argparse
import time
import subprocess

import bz2


def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("min", type=int, help = 'min ELO')
    parser.add_argument("max", type=int, help = 'max ELO')
    parser.add_argument("--count", type=int, help = 'number of games to output', default = 500000)

    parser.add_argument("output", type=str, help = 'output file name')

    parser.add_argument("targets", type=str, help = 'outputDir', nargs = '+')

    return parser.parse_args()

def getNextGame(f):
    out = ''
    isBad = False
    ncount = 0
    for l in f:
        out += l
        if l == '\n':
            ncount += 1
            if ncount > 1:
                break
        elif l.startswith('[Event '):
            if 'bullet' in l.lower():
                isBad = True
        elif l.startswith('[Result '):
            if '*' in l:
                isBad = True
        elif l.startswith('[WhiteElo '):
            try:
                eloW = int(l[11:-3])
            except ValueError:
                eloW = 0
                isBad = True
        elif l.startswith('[BlackElo '):
            try:
                eloB = int(l[11:-3])
            except ValueError:
                eloB = 0
                isBad = True
    try:
        return out, isBad, eloW, eloB
    except UnboundLocalError:
        return out, True, 0, 0


def readCollection(path, fout, minElo, maxElo, numRemaining):
    print(f"Reading {os.path.basename(path)}", end = '\r')
    numWritten = 0
    i = 0
    tstart = time.time()
    with bz2.open(path, 'rt') as f:
        while True:
            if numWritten % 1000 == 0:
                print(f"Reading {os.path.basename(path)[-30:]}, games read: {i}, games written: {numWritten}, in {time.time() - tstart:.2f}s need {numRemaining} more", end = '\r')
            i += 1
            game, isBad, eloW, eloB = getNextGame(f)
            if len(game) < 1:
                break
            elif isBad:
                continue
            elif eloW > maxElo or eloW < minElo:
                continue
            elif eloB > maxElo or eloB < minElo:
                continue
            fout.write(game)
            numWritten += 1
            numRemaining -= 1
            if numRemaining <= 0:
                break
    print(f"Done reading {os.path.basename(path)}, games read: {i}, games written: {numWritten}, in {time.time() - tstart:.2f}s need {numRemaining} more")
    return numWritten, numRemaining

def main():
    args = getArgs()

    print(f"Starting pgn extraction of {args.count} game between {args.min} {args.max} ELO to {args.output}")

    if len(os.path.dirname(args.output)) > 0:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)

    numRemaining = args.count
    with open(args.output, 'w') as fout:
        for tPath in args.targets:
            numWritten, numRemaining = readCollection(tPath, fout, args.min, args.max, numRemaining)
            if numRemaining <= 0:
                break
    print(f"{args.count - numRemaining} records written to {args.output}")

    print("starting clean")

    subprocess.run(['pgn-extract', '-7', '-C', '-N', '-#400000',  args.output])

    print("Done clean")


if __name__ == '__main__':
    main()
