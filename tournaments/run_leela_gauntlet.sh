#!/bin/bash

# Add -debug to see engine output

engine1="${1}"
times="10:00/40"

weightsDir="/w/225/reidmcy/chess/imitation-chess/networks"

leelasDir="/w/225/reidmcy/chess/imitation-chess/networks/leela_weights"

#No time control, but only look at 800 new nodes a round

mkdir -p leela_games/

mkdir -p "leela_games/${1}"

for engine2Path in /w/225/reidmcy/chess/imitation-chess/networks/leela_weights/*.gz;
do
    echo $engine2Path
    engine2Name=`python -c "import os.path;print(os.path.basename('${engine2Path}').split('.')[0])"`
    echo $engine2Name

    cutechess-cli -rounds 100 -tournament gauntlet -concurrency 4 -event "hai ${1} v leela ${engine2Name}"\
     -pgnout "leela_games/${1}/hai-${engine1}-v-leela-${engine2Name}.pgn" \
     -engine name="hai-${engine1}" cmd=lc0 arg="--threads=1" arg="--noise" arg="--weights=${weightsDir}/${engine1}-64x6-140000.pb.gz" arg="--no-ponder"\
     -engine name="leela-${engine2Name}" cmd=lc0 arg="--threads=1" arg="--noise" arg="--weights=${engine2Path}" arg="--no-ponder"\
     -each proto=uci tc="${times}"
 done
