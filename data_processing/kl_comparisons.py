import chess
import chess.uci

import pandas
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt

import json

import imitation_chess

import os
import re
import os.path

states = '../data/mapping_lichess_db_standard_rated_2018-10_collected.json'

netProbs = '../data/early_games_140000/'

def genHaiKLs(path):
    with open(states) as f:
        boards = [json.loads(l) for l in f]

    df_human = pandas.DataFrame(boards).set_index('board')

    with open(path) as f:
        results = [json.loads(l) for l in f]

    df_hai = pandas.DataFrame(results).set_index('board')

    df = df_hai.join(df_human)

    kl_prob_vals = []
    kl_n_vals = []
    human_probs = []
    comp_probs = []
    comp_ns = []
    boards = []
    for c, (i, row) in enumerate(df.iterrows()):
        if c % 1000 == 0:
            print("{:.2f}%".format(c / len(df) * 100), end = '\r', flush = True)
        stats = [imitation_chess.getMoveStats(s) for s in row['probs']]
        stats_prob = {s['move'] : s['prob'] for s in stats}
        stats_n = {s['move'] : s['N'] for s in stats}
        b = imitation_chess.fen(i)
        try:
            uciMap = imitation_chess.movesToUCI(row['counts'], b)
            countsUCI = { uciMap[k] : v for k,v in row['counts'].items()}
        except ValueError as e:
            #print("\n", e, flush=True)
            continue
        comp_prob = [v[1] for v in sorted(stats_prob.items(), key = lambda x : x[0]) if v[0] in countsUCI]
        comp_n_prob = [v[1] for v in sorted(stats_n.items(), key = lambda x : x[0]) if v[0] in countsUCI]

        a_comp = np.array(comp_prob)
        a_comp = a_comp / np.sum(a_comp)

        a_comp_n = np.array(comp_n_prob)
        #a_comp_n = a_comp_n / np.sum(a_comp_n)

        human_prob = [v[1] for v in sorted(countsUCI.items(), key = lambda x : x[0])]
        a_human = np.array(human_prob)
        a_human = a_human / np.sum(a_human)

        kl_prob_vals.append(scipy.stats.entropy(a_comp, a_human , base=2))
        kl_n_vals.append(scipy.stats.entropy(a_comp_n, a_human , base=2))
        boards.append(i)
        human_probs.append(a_human)
        comp_probs.append(a_comp)
        comp_ns.append(a_comp_n)


    df_kl = df.loc[boards].copy()
    df_kl['kl_prob'] = kl_prob_vals
    df_kl['kl_n'] = kl_n_vals
    df_kl['human_probs'] = list(human_probs)
    df_kl['comp_probs'] = list(comp_probs)
    df_kl['comp_ns'] = list(comp_ns)
    df_kl = df_kl.sort_values('kl_n', ascending=False)

    df_kl[['kl_prob', 'human_probs', 'comp_probs', 'comp_ns', 'kl_n']].to_csv(os.path.basename(path)[:-5] + '.csv')

def main():

    for e in os.scandir(netProbs):
        if e.name.endswith('json'):
            genHaiKLs(e.path)



if __name__ == '__main__':
    main()
