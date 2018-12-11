#!/bin/bash

engine1="${1}"
times="10:00/40"

parallel=8

weightsDir="/w/225/reidmcy/chess/imitation-chess/networks"

engine1Path="${weightsDir}/${engine1}"


if [ ! -f "${engine1Path}" ]; then
    echo "${engine1Path} not found!"
    exit 1
fi

echo "Using: ${engine1Path}"


engine1Name=`python -c "import os.path;print(os.path.basename('${weightsDir}/${engine1}').split('.')[0])"`

outputsDir="hai_games/${engine1Name}"

mkdir -p hai_games/

mkdir -p $outputsDir

echo "Running against stockfish"

for engine2Level in 0 5 10 15 20;
do

    echo $engine2Level

    cutechess-cli -rounds 100 -tournament gauntlet -concurrency $parallel \
    -event "hai ${engine1Name} v stockfish ${engine2Level}"\
    -pgnout "${outputsDir}/hai-${engine1Name}-v-stockfish-${engine2Level}.pgn" \
    -engine name="hai-${engine1Name}" cmd=lc0 arg="--threads=1" \
    arg="--noise" arg="--weights=${engine1Path}" arg="--no-ponder"\
    -engine name="stockfish-${engine2Level}" \
    cmd=stockfish initstr="setoption name Ponder value False\nsetoption name Ponder value False\nsetoption name Skill Level value ${engine2Level}"\
     -each proto=uci tc=$times 2>&1 | tee -a "${outputsDir}/hai-${engine1Name}-v-stockfish.txt"

done

echo "Running against leela"

for engine2Path in /w/225/reidmcy/chess/imitation-chess/networks/leela_weights/*.gz;
do
    engine2Name=`python -c "import os.path;print(os.path.basename('${engine2Path}').split('.')[0])"`
    echo $engine2Name

    cutechess-cli -rounds 100 -tournament gauntlet -concurrency $parallel \
    -event "hai ${engine1Name} v leela ${engine2Name}"\
    -pgnout "${outputsDir}/hai-${engine1Name}-v-leela-${engine2Name}.pgn" \
    -engine name="hai-${engine1Name}" cmd=lc0 arg="--threads=1" \
    arg="--noise" arg="--weights=${engine1Path}" arg="--no-ponder"\
     -engine name="leela-${engine2Name}" cmd=lc0 arg="--threads=1" arg="--noise" arg="--weights=${engine2Path}" arg="--no-ponder"\
     -each proto=uci tc=$times 2>&1 | tee -a "${outputsDir}/hai-${engine1Name}-v-leela.txt"
 done

echo "Done"
