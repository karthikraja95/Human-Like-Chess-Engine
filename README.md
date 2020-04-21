# Human-Like-Chess-Engine

## Abstract

We used supervised training to create a series of chess engines based on humans
play at different levels of skill. We compared them to other engines and to human
players and found that self-play trained engines would sometimes behave more
human-like than the supervised ones, although we believe this may be due to
improper hyperparameter selection. The three methods we used for comparing to
humans present a novel set of tools for evaluating human-like behaviour in complex
reinforcement learning systems and hope to develop them further.

## Goal
To make the chess engine that acts more like a human,
through supervised training and modification of it’s risk
sensitivity

## Reinforcement Learning Chess Engines

AlphaZero - Neural Network that evaluates on it’s
own, and uses the network to do a tree search
based on Predictive + Upper Bound Tree Search
(modification of UCB 1).
AlphaZero has been reimplemented in the open source
Leela Chess project
