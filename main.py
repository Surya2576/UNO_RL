from UnoCardGame import UnoGame, Player, Agent, Bot, GameResults
import json
import os
import matplotlib.pyplot as plt
import pickle

def save_results(results,win_loss,filename='game_results.txt'):
    f = open(filename,'w')
    # f.write(win_loss + "\n")
    for i in range(len(results)):
        f.write(str(i+1)+" ")
        f.write("Winner is " + results[i].winner + " ")
        #f.write()
        f.write("\n")
    f.close()




def main(num_games = 5000):
    print(os.getcwd())
    players = [Agent("Player 1","Agent"),Bot("Player 2","Agent")]
    game_results = []

    for game in range(num_games):
        qTable, winner, actions, finalState = UnoGame(players).gameplay()
        results = GameResults(qTable, winner,actions,finalState)
        game_results.append(results)
    
    win_loss = []
    for player in players:
        count = 0
        for i in range(num_games):
            if player.name == game_results[i].winner:
                count += 1
        win_loss.append("{} won {}".format(player.name,count))
    
    with open('trained_agent.pk1','wb') as file:
        pickle.dump(players[1],file)

    # UnoGame(players).gameplay()
    print(win_loss)
    save_results(game_results,str(win_loss))
    plot()

def plot(filename="game_results.txt"):
    with open("game_results.txt") as file:
        lines = file.readlines()
    
    game_numbers = []
    player1_wins = 0
    total_games = 0
    win_rates = []

    for line in lines:
        total_games += 1
        game_number = total_games
        game_numbers.append(game_number)

        if "Player 1" in line:
            player1_wins += 1
        
        win_rate = player1_wins / total_games
        win_rates.append(win_rate)
    plt.figure(figsize=(10, 5))
    plt.plot(game_numbers, win_rates, marker='o')
    plt.title('Win Rate of Player 1 Over Games')
    plt.xlabel('Game Number')
    plt.ylabel('Win Rate')
    plt.ylim(0, 1)  
    plt.grid()
    tick = total_games/10
    plt.xticks(range(0,total_games+1,int(tick)))
    plt.show()

if __name__ == "__main__":
    main()
