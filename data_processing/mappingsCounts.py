import re
import chess
import sys
import collections
import json
import csv
import os.path

target = sys

outputSuffix = '_collected'

minCount = 50

def writeBoard(boards, path, count):
    with open(path, 'w') as f:
        for b, d in boards.items():
            if sum(d.values()) >= count:
                json.dump({'board' : b, 'counts' : d}, f)
                f.write('\n')


def processMapping(target):
    dirname, filename = os.path.split(os.path.splitext(target)[0])
    outputName = os.path.join(dirname, f"{filename}{outputSuffix}.json")

    with open(target) as fin:
        reader = csv.DictReader(fin)
        counts = collections.defaultdict(dict)
        for i, l in enumerate(reader):
            b = ' '.join(l['board'].split(' ')[:2])
            try:
                counts[b][l['move']] += 1
            except KeyError:
                counts[b][l['move']] = 1
            if i % 10000 == 0:
                print(f"{i}: boards {len(counts)}", end = '\r')
            if i % 10000000 == 0:
                writeBoard(counts, outputName, minCount)
    print('\nDone')


def main():
    for targetPath in sys.argv[1:]:
        try:
            processMapping(targetPath)
        except FileExistsError:
            print("Skipping: ", targetPath)

if __name__ == '__main__':
    main()
