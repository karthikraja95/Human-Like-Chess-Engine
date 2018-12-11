#!/bin/bash

# Add -debug to see engine output

engine1="${1}" #lc0
#engine2="${2}" #stockfish
times="10:00/40"

weightsDir="/w/225/reidmcy/chess/imitation-chess/networks"


mkdir -p stockfish_games/

mkdir -p "stockfish_games/${1}"

for engine2Level in 0 5 10 15 20;
    do

    echo $engine2Level

    cutechess-cli -rounds 100 -tournament gauntlet -concurrency 4 -event "hai ${1} v stockfish ${2}"\
     -pgnout "stockfish_games/${1}/hai-${engine1}-v-stockfish-${engine2Level}.pgn" \
     -engine name="hai-${engine1}" cmd=lc0 arg="--threads=1" arg="--noise" arg="--weights=${weightsDir}/${engine1}-64x6-140000.pb.gz" arg="--no-ponder"\
     -engine name="stockfish-${engine2Level}" cmd=stockfish initstr="setoption name Ponder value False\nsetoption name Ponder value False\nsetoption name Skill Level value ${engine2Level}"\
     -each proto=uci tc=$time

done
