import chess
import re

moveRe = re.compile(r"^\S+")
probRe = re.compile(r"\(P: +([^)%]+)%\)")
uRe = re.compile(r"\(U: +([^)]+)\)")
qRe = re.compile(r"\(Q: +([^)]+)\)")
nRe = re.compile(r" N: +(\d+) \(")

fenComps = 'rrqn2k1/8/pPp4p/2Pp1pp1/3Pp3/4P1P1/R2NB1PP/1Q4K1 w KQkq - 0 1'.split()

def fen(s):
    splitS = s.split()
    return chess.Board(' '.join(splitS + fenComps[len(splitS):]))

def gameToFenSeq(game):
    headers = dict(game)
    moves = getBoardMoveMap(game)
    return {'headers' : headers, 'moves' : moves}

def getMoveStats(s):
    return {
        'move' : moveRe.match(s).group(0),
        'prob' : float(probRe.search(s).group(1)) / 100,
        'U' : float(uRe.search(s).group(1)),
        'Q' : float(qRe.search(s).group(1)),
        'N' : float(nRe.search(s).group(1)),
    }

def movesToUCI(moves, board):
    if isinstance(board, str):
        board = fen(board)
    moveMap = {}
    for m in moves:
        board.push_san(m)
        moveMap[m] = board.pop().uci()
    return moveMap
