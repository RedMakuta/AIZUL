from model import Player, GameState, PlayerState
from naive_player import NaivePlayer
import copy
import math
import random


class MCTSPlayer(Player):
    def __init__(self, _id, numberOfSimulations=100):
        super().__init__(_id)
        self.numberOfSimulations = numberOfSimulations

    def SelectMove(self, moves, game_state: GameState):
        # If there is only one move, just return it
        if len(moves) == 1:
            return moves[0]
        # Otherwise, use MCTS to select a move
        playerState = game_state.players[self.id]
        root = MonteCarloTreeSearchNode(game_state, playerState)
        action = root.bestAction(self.numberOfSimulations)
        # 'action' is the child node that was selected by MCTS, so the move that got there is the move we want to return
        return action.parentAction


class MonteCarloTreeSearchNode:
    def __init__(self, state: GameState, player: PlayerState, parent=None, parentAction=None):
        self.state = state
        self.player = player
        self.parent = parent
        self.parentAction = parentAction
        self.children = []
        self.numberOfVisits = 0
        self.results = {1: 0, -1: 0, 0: 0}
        self.untriedMoves = None
        self.untriedMoves = self.possible_moves()
        return

    # Gets the list of possible moves for this player at this state
    def possible_moves(self):
        self.untriedMoves = self.player.GetAvailableMoves(self.state)
        return self.untriedMoves

    def winLossRecord(self):
        wins = self.results[1]
        losses = self.results[-1]
        return wins - losses

    def numberOfVisits(self):
        return self.numberOfVisits

    # Is the game over (rows filled), used for determining end of leaf node simulation
    def isRoundOver(self, gameState: GameState):
        return not gameState.TilesRemaining()

    def isFullyExpanded(self):
        return len(self.untriedMoves) == 0

    # Uses UCB to select which child node is the most 'promising'
    def bestChild(self, explorationParameter=0.1):
        bestChild = None
        bestValue = float("-inf")
        for c in self.children:
            UCB = c.winLossRecord() + explorationParameter * math.sqrt(math.log(self.numberOfVisits) / c.numberOfVisits)
            if UCB > bestValue:
                bestChild = c
                bestValue = UCB
        return bestChild

    # Expansion
    def expand(self):
        nextMove = self.untriedMoves.pop()
        nextGameState = copy.deepcopy(self.state)
        nextGameState.ExecuteMove(self.player.id, nextMove)
        child_node = MonteCarloTreeSearchNode(nextGameState, nextGameState.players[1-self.player.id], parent=self, parentAction=nextMove)
        self.children.append(child_node)
        return child_node

    def expansionPolicy(self):
        currentNode = self
        while not currentNode.isRoundOver(currentNode.state):
            if not currentNode.isFullyExpanded():
                return currentNode.expand()
            else:
                currentNode = currentNode.bestChild()
        return currentNode

    # Simulation
    def simulate(self):
        simulatedState = copy.deepcopy(self.state)
        currentPlayer = self.player.id
        while not self.isRoundOver(simulatedState):
            possible_moves = simulatedState.players[currentPlayer].GetAvailableMoves(simulatedState)
            chosenMove = self.simulationPolicy(possible_moves, simulatedState)
            simulatedState.ExecuteMove(currentPlayer, chosenMove)
            currentPlayer = 1 - currentPlayer
        # Calculate the scores to see who is winning, including end of game bonuses
        ourself = simulatedState.players[self.player.id]
        opponent = simulatedState.players[1-self.player.id]
        ourself.ScoreRound()
        ourself.EndOfGameScore()
        opponent.ScoreRound()
        opponent.EndOfGameScore()
        ourselfScore = ourself.score
        opponentScore = opponent.score
        if ourselfScore > opponentScore:
            return 1
        elif ourselfScore < opponentScore:
            return -1
        else:
            return 0

    # What move to pick when simulating
    def simulationPolicy(self, possible_moves, state: GameState):
        # Option 1: Pick a random move
        #return random.choice(possible_moves)
        # Option 2: Use the Naive player logic (especially good since that's who we're playing against)
        Naive = NaivePlayer(1)
        return Naive.SelectMove(possible_moves, state)

    # Backpropagation
    def backpropagate(self, result):
        self.numberOfVisits += 1
        self.results[result] += 1
        if self.parent:
            self.parent.backpropagate(result)

    def bestAction(self, numberOfSimulations):
        for simCount in range(numberOfSimulations):
            nodeToSimulate = self.expansionPolicy()
            outcome = nodeToSimulate.simulate()
            nodeToSimulate.backpropagate(outcome)
        return self.bestChild(explorationParameter=0)
