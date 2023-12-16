import random
from model import GameRunner, Player
from iplayer import InteractivePlayer
from naive_player import NaivePlayer
from mcts_player import MCTSPlayer
from utils import *

numberOfIterations = 10
MCTS_Scores = []
Naive_Scores = []
for i in range(numberOfIterations):
    print(f"Iteration {i}")
    players = [MCTSPlayer(0), NaivePlayer(1)]
    seed = random.randint(0, 1000000)
    gr = GameRunner(players, seed)
    activity = gr.Run(False)

    MCTS_Scores.append(activity[0][0])
    Naive_Scores.append(activity[1][0])

    #print("Player 0 score is {}".format(activity[0][0]))
    #print("Player 1 score is {}".format(activity[1][0]))
print(f"Average MCTS score: {sum(MCTS_Scores)/numberOfIterations}")
print(f"Average Naive score: {sum(Naive_Scores)/numberOfIterations}")
print(MCTS_Scores)
print(Naive_Scores)
