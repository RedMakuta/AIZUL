# Written by Michelle Blom, 2019
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
import random

from model import GameRunner, Player
from iplayer import InteractivePlayer
from naive_player import NaivePlayer
from mcts_player import MCTSPlayer
from utils import *

players = [MCTSPlayer(0, 10000), NaivePlayer(1)]

gr = GameRunner(players, random.randint(0, 1000000))

activity = gr.Run(True)

print("Player 0 score is {}".format(activity[0][0]))
print("Player 1 score is {}".format(activity[1][0]))
if len(players) > 2:
    print("Player 2 score is {}".format(activity[2][0]))
if len(players) > 3:
    print("Player 3 score is {}".format(activity[3][0]))


#print("Player 0 round-by-round activity")
#player_trace = activity[0][1]
#for r in range(len(player_trace.moves)):
#    print("ROUND {}".format(r+1))
#    for move in player_trace.moves[r]:
#        print(MoveToString(0, move))
#    print("Score change {}".format(player_trace.round_scores[r]))

#print("Bonus points {}".format(player_trace.bonuses))
