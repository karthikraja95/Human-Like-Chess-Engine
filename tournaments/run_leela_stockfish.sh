#!/bin/bash

# Add -debug to see engine output

times="10:00/40"


#No time control, but only look at 800 new nodes a round

mkdir -p leela_v_stockfish_games/


for engine1Level in 0 5 10 15 20;
do

for engine2Path in /w/225/reidmcy/chess/imitation-chess/networks/leela_weights/*.gz;
do
    echo $engine2Path
    engine2Name=`python -c "import os.path;print(os.path.basename('${engine2Path}').split('.')[0])"`
    echo $engine2Name

    mkdir -p "leela_v_stockfish_games/${engine2Name}"

    cutechess-cli -rounds 100 -tournament gauntlet -concurrency 4 -event "stockfish ${engine1Level} v leela ${engine2Name}"\
     -pgnout "leela_v_stockfish_games/${engine2Name}/stockfish-${engine1Level}-v-leela-${engine2Name}.pgn" \
     -engine name="stockfish-${engine1Level}" cmd=stockfish initstr="setoption name Ponder value False\nsetoption name Ponder value False\nsetoption name Skill Level value ${engine1Level}"\
     -engine name="leela-${engine2Name}" cmd=lc0 arg="--threads=1" arg="--noise" arg="--weights=${engine2Path}" arg="--no-ponder"\
     -each proto=uci tc="${times}"
 done

done
