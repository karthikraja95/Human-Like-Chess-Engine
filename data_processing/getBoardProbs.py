import imitation_chess

import json
import os
import os.path

import sys
import multiprocessing

boardStates = '../data/mapping_lichess_db_standard_rated_2018-10_collected.json'
networksDir = '/u/reidmcy/w/chess/imitation-chess/networks'
ouputDir = '../data/early_games_140000'

num_engines = 16

nodesPerBoard = 10000

def jsonOutput(results, board):
    bestmove = str(results[0].bestmove)
    ponderedmove = str(results[0].ponder)
    return json.dumps({'bestmove' : bestmove, 'ponderedmove' : ponderedmove,
    'probs' : results[1], 'board' : board})

def EngineProcess(enginePath, boards, Q):
    engine = imitation_chess.EngineHandler('lc0', enginePath, threads = 1)
    for b in boards:
        board = imitation_chess.fen(b)
        ret = engine.getBoardProbs(board, movetime = 10000 * 30, nodes = nodesPerBoard)
        Q.put(jsonOutput(ret, b))
    Q.put(False)
    return


def engineRun(targetNetwork):
    outputName = os.path.join(ouputDir, os.path.basename(targetNetwork)[:-6] + '.json')

    print(f"Starting on: {targetNetwork} to {outputName}")

    os.makedirs(ouputDir, exist_ok = True)

    with open(boardStates) as f:
        boards = [json.loads(l) for l in f]

    sortedBoards = sorted(boards, key = lambda x : sum(x['counts'].values()))

    print(f"Loaded and sorted {len(sortedBoards)} board states")

    splitBoards = {i : [] for i in range(num_engines)}
    for i, b in enumerate(sortedBoards):
        splitBoards[i % num_engines].append(b['board'])

    print("Split into:", {k : len(v) for k, v in splitBoards.items()})

    processes = []
    mainQ = multiprocessing.Queue()

    for i in range(num_engines):
        print("Starting process: ", i)
        p = multiprocessing.Process(target=EngineProcess, args=(targetNetwork, splitBoards[i], mainQ))
        p.start()
        processes.append(p)

    print("Starting main loop")
    num_done_procs = 0
    num_done_boards = 0
    while True:
        val = mainQ.get()

        if val:
            num_done_boards += 1
            with open(outputName, 'a') as f:
                f.write(val)
                f.write('\n')
            print(f"Done {num_done_boards} boards", end ='\r')
        else:
            num_done_procs += 1
            print(f"\nProcess {num_done_procs} of {num_engines} complete")
            if num_done_procs == num_engines:
                break

    print("\nAll done, joining")
    for p in processes:
        p.join()
    print("Done")

def main():

    engines = []
    for e in os.scandir(networksDir):
        if e.name.endswith('-64x6-140000.pb.gz'):
            engines.append(e.path)

    for engine in engines:
        print(f"Starting {engine}")
        engineRun(engine)
        print(f"Done {engine}")

    print("Done All engines")

if __name__ == '__main__':
    main()
