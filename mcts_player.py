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
        self.untriedMoves = self.possibleMoves()
        return

    # Gets the list of possible moves for this player at this state
    def possibleMoves(self):
        return self.player.GetAvailableMoves(self.state)

    # W - L
    def winLossRecord(self):
        wins = self.results[1]
        losses = self.results[-1]
        return wins - losses

    # How many times this node has been expanded
    def numberOfVisits(self):
        return self.numberOfVisits

    # Is the game over (rows filled), used for determining end of leaf node simulation
    def isRoundOver(self, gameState: GameState):
        return not gameState.TilesRemaining()

    # Uses UCT (I think??) to select which child node is the most 'promising'
    def bestChild(self, explorationParameter=0.1):
        bestChild = None
        bestValue = float("-inf")
        for child in self.children:
            value = (child.results[1]/child.numberOfVisits) + explorationParameter * math.sqrt(2 * math.log(self.numberOfVisits) / child.numberOfVisits)
            if value > bestValue:
                bestChild = child
                bestValue = value
        return bestChild

    # Expansion
    def expand(self):
        nextMove = self.untriedMoves.pop()
        nextGameState = copy.deepcopy(self.state)
        nextGameState.ExecuteMove(self.player.id, nextMove)
        childNode = MonteCarloTreeSearchNode(nextGameState, nextGameState.players[1-self.player.id], parent=self, parentAction=nextMove)
        self.children.append(childNode)
        return childNode

    # Expand nodes by their UCT(?) value first, until you reach a leaf
    def expansionPolicy(self):
        currentNode = self
        while not currentNode.isRoundOver(currentNode.state):
            if len(currentNode.untriedMoves) > 0:
                return currentNode.expand()
            else:
                currentNode = currentNode.bestChild()
        return currentNode

    # Simulation
    def simulate(self):
        simulatedState = copy.deepcopy(self.state)
        currentPlayer = self.player.id
        while not self.isRoundOver(simulatedState):
            possibleMoves = simulatedState.players[currentPlayer].GetAvailableMoves(simulatedState)
            chosenMove = self.simulationPolicy(possibleMoves, simulatedState)
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

    # Do a bunch of expansion and simulation and then pick the favorite node
    def bestAction(self, numberOfSimulations):
        for simCount in range(numberOfSimulations):
            nodeToSimulate = self.expansionPolicy()
            outcome = nodeToSimulate.simulate()
            nodeToSimulate.backpropagate(outcome)
        return self.bestChild(explorationParameter=0)
