#!/bin/bash

# Add -debug to see engine output

engine1="${1}"
engine2="${2}"

weightsDir="/w/225/reidmcy/chess/imitation-chess/networks"


#No time control, but only look at 800 new nodes a round

cutechess-cli -rounds 100 -tournament gauntlet -concurrency 4 -event "hai ${1} v hai ${2}"\
 -pgnout "hai-${engine1}-v-hai-${engine2}.pgn" \
 -engine name="hai-${engine1}" cmd=lc0 arg="--threads=1" arg="--noise" arg="--weights=${weightsDir}/${engine1}-64x6-140000.pb.gz" arg="--no-ponder"\
 -engine name="hai-${engine2}" cmd=lc0 arg="--threads=1" arg="--noise" arg="--weights=${weightsDir}/${engine2}-64x6-140000.pb.gz" arg="--no-ponder"\
 -each proto=uci tc=40/40
