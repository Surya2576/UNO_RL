import random
import math
import numpy as np
import time

class UnoGame:
    
    colors = ["Red","Blue","Green","Yellow"]
    values = [0,1,2,3,4,5,6,7,8,9]
    specials = ["Draw Two","Reverse","Skip"]
    wilds = ["Wild","Wild Draw Four"]

    def __init__(self,players=None):

        self.deck = self.build()
        self.shuffle()
        self.winner = ""

        if players is None:
            self.players = []
            self.numPlayers = 0
        else:
            self.players = players
            self.numPlayers = len(players)

        self.setUp()
        self.turn = 0
        self.direction = 1
        self.playing = True
        
        self.discards = []
        self.discards.append(self.deck.pop(0))

        self.currentColor = self.readCard(self.discards[-1])[0]
        self.currentValue = self.readCard(self.discards[-1])[1]

        while self.currentColor == "Wild":
            self.deck.append(self.discards.pop(-1))
            self.discards.append(self.deck.pop(0))
            self.currentColor = self.readCard(self.discards[-1])[0]
            self.currentValue = self.readCard(self.discards[-1])[1]
        
        while self.currentValue in self.specials:
            self.deck.append(self.discards.pop(-1))
            self.discards.append(self.deck.pop(0))
            self.currentColor = self.readCard(self.discards[-1])[0]
            self.currentValue = self.readCard(self.discards[-1])[1]

        print("Opening card is {}\n".format(self.discards[-1]))
        # self.gameplay()
    
    def setUp(self):
        if not self.players:
            numPlayers = int(input("Number of Players? "))
            while numPlayers < 2 or numPlayers > 7:
                numPlayers = int(input("Invalid. Please enter a number bewteen 2-7. Number of Players? "))
                self.numPlayers = numPlayers
            for player in range(numPlayers):
                self.players.append(Player("Player " + str((player+1)),"Human :)"))
        for player in range(self.numPlayers):
            self.players[player].hand.extend(self.deal(5))

    def build(self):
        deck = []
        for color in self.colors:
            for value in self.values:
                cardValue = "{} {}".format(color, value)
                deck.append(cardValue)
                if value != 0:
                    deck.append(cardValue)

            for special in self.specials:
                cardValue = "{} {}".format(color, special)
                deck.append(cardValue)
                deck.append(cardValue)

            deck.append(self.wilds[0])
            deck.append(self.wilds[1])
        return deck

    def shuffle(self):
        # for card in range(len(self.deck)):
        #     rand = random.randint(0,107)
        #     self.deck[card], self.deck[rand] = self.deck[rand], self.deck[card]
        random.shuffle(self.deck)
        return self.deck

    def deal(self,num):
        if len(self.deck) <= num:
            temp = self.deck
            self.deck = self.discards
            self.discards.append(self.deck.pop(-1))
            self.shuffle()
        dealtCards = []
        for i in range(num):
            dealtCards.append(self.deck.pop(0))
        return dealtCards

    def canPlay(self, color, value, hand):
        for card in hand:
            # print("checking if {} in {}".format(color,card))
            if "Wild" in card:
                return True
            elif color in card:
                return True
            elif value in card:
                return True
        return False

    def readCard(self, card):
        reading = card.split(" ",1)
        if len(reading) == 1:
            return [reading[0],"Any"]
        else:
            return [reading[0],reading[1]]

    def nextTurn(self,turn,direction):
        nextTurn = turn + direction
        if nextTurn > (self.numPlayers - 1):
            nextTurn = 0
        elif nextTurn < 0:
            nextTurn = self.numPlayers - 1
        return nextTurn
    
    def special(self, color, value, controller, colorChoice):
        if color == "Wild":
            print("")
            for x in range(len(self.colors)):
                print("{} {}".format(x+1,self.colors[x]))
            print("")
            if controller == "Agent":
                self.currentColor = self.colors[colorChoice]
            else:
                newColor = int(input("What color would you like to choose? "))
                while newColor < 1 or newColor > 4:
                    newColor = int(input("Invalid input. What color would you like to choose? "))
                self.currentColor = self.colors[newColor-1]
            print("The new chosen color is {}".format(self.currentColor))
        
        if value == "Reverse":
            self.direction *= -1

        elif value == "Skip":
            nextTurn = self.turn + self.direction
            if nextTurn > (self.numPlayers - 1):
                self.turn = 0
            elif nextTurn < 0:
                self.turn = self.numPlayers - 1
            else:
                self.turn += self.direction
        
        elif value == "Draw Two":
            nextTurn = self.nextTurn(self.turn,self.direction)
            self.players[nextTurn].hand.extend(self.deal(2))
            print ("{} drew 2 cards".format(self.players[nextTurn].name))
        
        elif value == "Draw Four":
            nextTurn = self.nextTurn(self.turn,self.direction)
            self.players[nextTurn].hand.extend(self.deal(4))
            print ("{} drew 4 cards".format(self.players[nextTurn].name))
            
    def gameplay(self):
        actions = []
        while self.playing:
            for i in range(self.numPlayers):
                if len(self.players[i].hand) == 0:
                    print ("{} WINS !!!".format(self.players[i].name))
                    self.winner = self.players[i].name
                    self.playing = False
            if self.playing == False:
                return (self.players[0].qTable, self.winner,actions,self.players[self.turn].state(self.players,self.turn,[self.currentColor,self.currentValue],self.nextTurn(self.turn,self.direction)))
            self.players[self.turn].showHand()
            print("Card on top of discard pile: {}".format(self.discards[-1]))
            if "Wild" in self.discards[-1]:
                print("Chosen color is {}".format(self.currentColor))
            if self.canPlay(self.currentColor,self.currentValue,self.players[self.turn].hand):
                
                if self.players[self.turn].controller == "Agent":
                    state = self.players[self.turn].state(self.players,self.turn,[self.currentColor,self.currentValue],self.nextTurn(self.turn,self.direction))
                    stateKey = self.players[self.turn].getStateKey(state)
                    action = self.players[self.turn].chooseAction(state,stateKey)
                    if isinstance(self.players[self.turn],Agent):
                        reward = self.players[self.turn].calculateReward(state,action)
                        actions.append({
                            "player": self.players[self.turn].name,
                            "action": action,
                            "card": self.discards[-1]
                        })
                    if action == 2:
                        print("{} chose to draw".format(self.players[self.turn].name))
                        self.players[self.turn].hand.extend(self.deal(1))
                    else:
                        cardChosen = action[1]
                        colorChoice = 0
                        if "Wild" in self.players[self.turn].hand[cardChosen]:
                            colorChoice = action[2]
                        print("{} played {}".format(self.players[self.turn].name,self.players[self.turn].hand[cardChosen]))
                        self.discards.append(self.players[self.turn].play(cardChosen))
                        self.currentColor = self.readCard(self.discards[-1])[0]
                        self.currentValue = self.readCard(self.discards[-1])[1]
                        preSpecialTurn = self.turn
                        self.special(self.currentColor,self.currentValue, self.players[self.turn].controller, colorChoice)
                    if isinstance(self.players[preSpecialTurn],Agent):
                        nextState = self.players[preSpecialTurn].state(self.players,preSpecialTurn,[self.currentColor,self.currentValue],self.nextTurn(preSpecialTurn,self.direction))
                        nextStateKey = self.players[preSpecialTurn].getStateKey(nextState)
                        self.players[preSpecialTurn].updateQValue(stateKey, action, reward, nextStateKey)
                else:
                    play = int(input("Do you want to: 1 Play or 2 Draw? (enter 1 or 2) "))
                    while play != 1 and play != 2:
                        play = int(input("Invalid input. Do you want to: 1 Play or 2 Draw? (enter 1 or 2) "))
                    if play == 1:
                        cardChosen = int(input("Which card do you want to play? ")) - 1
                        while cardChosen+1 > len(self.players[self.turn].hand) or cardChosen+1 < 1:
                            cardChosen = int(input("Not a valid card. Which card do you want to play? ")) - 1
                        while not self.canPlay(self.currentColor, self.currentValue, [self.players[self.turn].hand[cardChosen]]):
                            cardChosen = int(input("Not a valid card. Which card do you want to play? ")) - 1
                        print("{} played {}".format(self.players[self.turn].name,self.players[self.turn].hand[cardChosen]))
                        self.discards.append(self.players[self.turn].play(cardChosen))
                        self.currentColor = self.readCard(self.discards[-1])[0]
                        self.currentValue = self.readCard(self.discards[-1])[1]
                        self.special(self.currentColor,self.currentValue, self.players[self.turn].controller, 0)
                    elif play == 2:
                        print("{} chose to draw".format(self.players[self.turn].name))
                        self.players[self.turn].hand.extend(self.deal(1))
                
                

            else:
                print("!!! You can't play. You have to draw a card.!!!")
                # play = int(input("!!! You can't play. You have to draw a card. Please enter 2 to draw a card!!! "))
                # while play != 2:
                #     play = int(input("!!!Invalid Input. You can't play. You have to draw a card. Please enter 2 to draw a card!!! "))
                self.players[self.turn].hand.extend(self.deal(1))
            print("")

            if len(self.players[self.turn].hand) == 1:
                print ("UNO ~ Player {}".format(self.turn+1))

            
            nextTurn = self.turn + self.direction
            if nextTurn > (self.numPlayers - 1):
                self.turn = 0
            elif nextTurn < 0:
                self.turn = self.numPlayers - 1
            else:
                self.turn += self.direction

            print("")

class Player:
    def __init__(self, name: str, controller):
        self.name = name
        self.hand = []
        self.controller = controller

    def showHand(self):
        print("{}'s Turn".format(self.name))
        print("Your Hand")
        print("-- -- -- -- -- --")
        y = 1
        for card in self.hand:
            print("{} {}".format(y,card))
            y += 1
        print("-- -- -- -- -- --")
        print("")

    def play(self,value):
        return self.hand.pop(value)

class Agent(Player):
    def __init__(self,name,controller):
        self.actions = [1,2,[0,1,2,3]]
        self.qTable = {}
        self.name = name
        self.controller = controller
        self.hand = []
        self.learningRate = 0.1
        self.discountFactor = 0.9
        self.epsilon = 1.0
        self.epsilonDecay = 0.99
        self.minEpsilon = 0.1
    
    def state(self, players, agentIndex, currColorAndVal, nextTurn):
        self.numCards = len(self.hand)
        self.nextPlayer = players[nextTurn]
        suits = ["Red","Blue","Green","Yellow","Wild"]
        self.sortedHand = []
        firstHandSort = []
        self.currentColor = currColorAndVal[0]
        self.currentValue = currColorAndVal[1]
        self.currColorAndVal = currColorAndVal
        for suit in suits:
            for card in self.hand:
                if card.split(" ",1)[0] == suit:
                    firstHandSort.append(card)
            self.sortedHand.extend(sorted(firstHandSort))
            firstHandSort.clear()
        
        numOppCards = []
        for i in range(len(players)):
            if i != agentIndex:
                numOppCards.append(len(players[i].hand))
        state = [self.numCards, self.sortedHand, numOppCards, self.currentColor, self.currentValue, self.currColorAndVal, self.nextPlayer]
        # print("CURR COLOR AND VAL IS {}".format(self.currColorAndVal))
        return state
    
    def getStateKey(self,state):
        return str(state)

    def playableCards(self, currColorAndVal):
        playableCards = []
        color = currColorAndVal[0]
        value = currColorAndVal[1]
        for card in self.sortedHand:
            if "Wild" in card:
                playableCards.append(card)
            elif color in card:
                playableCards.append(card)
            elif value in card:
                playableCards.append(card)
        return playableCards

    def chooseAction(self, state, stateKey):
        if random.random() < self.epsilon:
            playable = self.playableCards(state[5])
            if playable:
                # if len(self.hand) < 10:
                #     mainAction = random.choice([1,2])
                # else:
                #     mainAction = 1
                # if mainAction == 1:
                chosenCard = random.choice(playable)
                index = self.hand.index(chosenCard)
                if chosenCard.split(" ",1)[0] == "Wild":
                    return (1, index, random.choice(self.actions[2]))
                return (1,index)
                # elif mainAction == 2:
                #     return 2
            else:
                return 2

        else:
            qValues = self.qTable.get(stateKey,{})

            if not qValues:
                playable = self.playableCards(state[5])
                if playable:
                    mainAction = random.choice([1,2])
                    if mainAction == 1:
                        chosenCard = random.choice(playable)
                        index = self.hand.index(chosenCard)
                        if chosenCard.split(" ",1)[0] == "Wild":
                            return (1, index, random.choice(self.actions[2]))
                        return (1,index)
                    elif mainAction == 2:
                        return 2
                else:
                    return 2

            drawValue = qValues.get(2,0)

            playable = self.playableCards(state[5])
            playValue = [qValues.get((1,index),0) for index in range(len(self.hand))]

            if drawValue > max(playValue, default = 0):
                return 2
            
            optimalPlay = max(playable, key = lambda card: qValues.get((1, self.hand.index(card)),0))
            index = self.hand.index(optimalPlay)

            if optimalPlay(" ",1)[0] == "Wild":
                return (1, index, random.choice(self.actions[2]))
            return (1, index)
    
    def calculateReward(self,state,action):
        if action == 2:
            return -20
        elif action[0] == 1:
            reward = 0
            cardType = self.hand[action[1]].split(" ",1)[-1]
            if len(self.hand) > 5:
                reward += (5*(math.log(len(self.hand))/2))
            else:
                reward += 20

            if len(self.hand) == 1:
                reward += 100
            
            if cardType in ["Skip","Reverse","Draw Two","Draw Four"]:
                if len(state[6].hand) <= len(self.hand):
                    if len(state[6].hand) == 3:
                        if cardType == "Skip" or cardType == "Reverse":
                            reward += 8
                        if cardType == "Draw Two":
                            reward += 10
                        if cardType == "Draw Four":
                            reward += 16
                    elif len(state[6].hand) == 2:
                        if cardType == "Skip" or cardType == "Reverse":
                            reward += 12
                        if cardType == "Draw Two":
                            reward += 18
                        if cardType == "Draw Four":
                            reward += 24
                    elif len(state[6].hand) == 1:
                        if cardType == "Skip" or cardType == "Reverse":
                            reward += 20
                        if cardType == "Draw Two":
                            reward += 30
                        if cardType == "Draw Four":
                            reward += 40
        return reward
        

    def updateQValue(self,stateKey,action,reward,nextStateKey):
        currentQ = self.qTable.get(stateKey,{}).get(action,0)
        nextMaxQ = max(self.qTable.get(nextStateKey,{}).values(),default=0)
        newQ = currentQ + self.learningRate * (reward + self.discountFactor*nextMaxQ - currentQ)

        if stateKey not in self.qTable:
            self.qTable[stateKey] = {}
        self.qTable[stateKey][action] = newQ

class Bot(Player):
    def __init__(self,name,controller):
        self.actions = [1,2,[0,1,2,3]]
        self.name = name
        self.controller = controller
        self.hand = []

    def state(self, players, agentIndex, currColorAndVal, nextTurn):
        self.numCards = len(self.hand)
        self.nextPlayer = players[nextTurn]
        suits = ["Red","Blue","Green","Yellow","Wild"]
        self.sortedHand = []
        firstHandSort = []
        self.currentColor = currColorAndVal[0]
        self.currentValue = currColorAndVal[1]
        self.currColorAndVal = currColorAndVal
        for suit in suits:
            for card in self.hand:
                if card.split(" ",1)[0] == suit:
                    firstHandSort.append(card)
            self.sortedHand.extend(sorted(firstHandSort))
            firstHandSort.clear()
        
        numOppCards = []
        for i in range(len(players)):
            if i != agentIndex:
                numOppCards.append(len(players[i].hand))
        state = [self.numCards, self.sortedHand, numOppCards, self.currentColor, self.currentValue, self.currColorAndVal]
        # print("CURR COLOR AND VAL IS {}".format(self.currColorAndVal))
        return state
    
    def getStateKey(self,state):
        return str(state)
    
    def playableCards(self, currColorAndVal):
        playableCards = []
        color = currColorAndVal[0]
        value = currColorAndVal[1]
        for card in self.sortedHand:
            if "Wild" in card:
                playableCards.append(card)
            elif color in card:
                playableCards.append(card)
            elif value in card:
                playableCards.append(card)
        return playableCards

    def chooseAction(self, state, stateKey):
        playable = self.playableCards(state[5])
        if playable:
            chosenCard = playable[0]
            index = self.hand.index(chosenCard)
            if chosenCard.split(" ",1)[0] == "Wild":
                return (1, index, random.choice(self.actions[2]))
            return (1,index)
        else:
            return 2

class GameResults:
    def __init__(self,qTable,winner,actions,final_state):
        self.winner = winner
        self.actions = actions
        self.final_state = final_state
        self.qTable = qTable
    
    def to_dict(self):
        return {
            "winner": self.winner,
            "actions":self.actions,
            "final_state":self.final_state,
            "this game's q.Table": self.qTable
        }


    

