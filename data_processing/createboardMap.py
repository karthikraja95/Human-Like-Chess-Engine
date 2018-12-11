import imitation_chess
import chess

gamesPath = '../data/lichess_db_standard_rated_2018-09.pgn.bz2'
outputPath = '../data/mapping_2018-09.csv'

def main():
    games = imitation_chess.GamesFile(gamesPath)
    with open(outputPath, 'w') as f:
        f.write("board,move,game,BlackElo,WhiteElo\n")
        for i, g in enumerate(games):
            d = imitation_chess.getBoardMoveMap(g)
            gameID = g.headers['Site'].split('/')[-1]
            BlackElo = g.headers['BlackElo']
            WhiteElo = g.headers['WhiteElo']
            for k, v in d.items():
                f.write(f"{k},{v},{gameID},{BlackElo},{WhiteElo}\n")
            if i % 1000 == 0:
                print(f"{i}: {gameID}")
                f.flush()

if __name__ == '__main__':
    main()
