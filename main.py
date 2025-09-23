from collections import Counter
from typing import Literal
import json
import time
import sys
import os

players = {}
nextprint = ""

def get_numbers(input: str):
    user_input = input
    numbers = [int(num.strip()) for num in user_input.split(",")]
    return numbers

def num_to_resource(num: int):
    if num == 1:
        return "Wood"
    elif num == 2:
        return "Stone"
    elif num == 3:
        return "Wheet"
    elif num == 4:
        return "Sheep"
    elif num == 5:
        return "Ore"
    
def add_player(name: str):
    global players
    players[name] = {"order":len(players)+1}

def get_player_order(order: int):
    global players
    for name, info in players.items():
        if info.get("order") == order:
            return name
    return None

def get_player_resources(name: str):
    global players
    if name not in players:
        raise ValueError(f"Player {name} does not exist.")
    elif "resources" not in players[name]:
        return []
    else:
        return players[name]["resources"]

def format_resources(name: str, resources: list):
    global players
    counts = Counter(resources)
    formatted = " ".join(f"{num}:{num_to_resource(num)} = {counts[num]}," for num in sorted(counts))
    return f"{name}: {formatted}"

def add_resource(name: str, resources: list):
    global players
    processed = []
    for r in resources:
        if r > 6 or r < 1:
            raise ValueError("Invalid resource")
        elif r == 6:
            choice = input(f"Resource '(6) gold' for {name} detected! Enter choice: ")
            if not choice or choice == 6:
                raise ValueError("Invalid replacement")
            processed.append(int(choice))
        else:
            processed.append(r)

    if "resources" not in players[name]:
        players[name]["resources"] = processed.copy()
    else:
        players[name]["resources"].extend(processed)

def remove_resource(name: str, resource: list):
    global players
    if name not in players:
        raise ValueError(f"Player {name} does not exist.")
    elif "resources" not in players[name]:
        raise ValueError(f"Player {name} has no resources.")
    else:
        for r in resource:
            if r > 0 and r < 7:
                players[name]["resources"].remove(r)
            else:
                raise ValueError("Invalid resource")
            
def trade(name1: str, name2: str, resource1: list, resource2: list):
    global players
    if name1 not in players or name2 not in players:
        print("Player does not exist.")
        return
    if "resources" not in players[name1] or "resources" not in players[name2]:
        print("Players have no resources.")
        return
    for r in resource1:
        if r not in players[name1]["resources"]:
            print(f"{name1} does not have resource {r}. Trade canceled.")
            return
    for r in resource2:
        if r not in players[name2]["resources"]:
            print(f"{name2} does not have resource {r}. Trade canceled.")
            return
    add_resource(name1, resource2)
    remove_resource(name2, resource2)
    add_resource(name2, resource1)
    remove_resource(name1, resource1)


def add_source(name: str, number: Literal[2,3,4,5,6,7,8,9,10,11,12], resource: Literal[1,2,3,4,5,6]):
    global players
    if resource > 0 and resource < 7 and number > 1 and number < 13 and name in players:
        if "sources" not in players[name]:
            players[name]["sources"] = {}

        if number not in players[name]["sources"]:
            players[name]["sources"][number] = []

        players[name]["sources"][number].append(resource)

def new_roll(p, number):
    global players
    global nextprint
    number = int(number)
    nextprint = ""
    for name, data in players.items():
        sources = data.get("sources", {})
        if number in sources:
            resources_to_add = sources[number].copy()
            add_resource(name, resources_to_add)
            nextprint = nextprint +f"Added {resources_to_add, num_to_resource(resources_to_add) } to {name} for roll {number}\n"
        else:
            pass
def main():
    global players
    turn = 1
    while True:
        nextturn = 0
        while nextturn == 0:
            if sys.platform.startswith("win"):
                os.system("cls")  #
            else:
                os.system("clear")  
            print(nextprint)
            player = 0

            if turn == 1:
                player = get_player_order(1)
                print("Starting player:", player)
            else:
                player = get_player_order((turn - 1) % len(players) + 1)
                print("Current player:", player)

            for name in players:
                print(format_resources(name, get_player_resources(name)))

            print("""\nChoose an option: 
    1 - Build
    2 - Trade
    3 - Steal
    4 - Split
    5 - Add source
    6 - Add resources
    7 - remove latest source
    8 - Next turn
    9 - Input full data\n""")
            
            print("Debug (full list of players and data):")
            print(players)

            choice = int(input("Enter choice (1-8): "))
            if choice == 1: #build
                buildingchoice = input("Enter building (VI, CI, CA, ST, SH or 1-5): ")
                if buildingchoice == "q":
                    continue
                elif buildingchoice.lower() in ("vi", "1"):
                    remove_resource(player, [1,2,3,4])
                elif buildingchoice.lower() in ("ci", "2"):
                    remove_resource(player, [3,3,5,5,5])
                elif buildingchoice.lower() in ("ca", "3"):
                    remove_resource(player, [3,4,5])
                elif buildingchoice.lower() in ("st", "4"):
                    remove_resource(player, [1,2])
                elif buildingchoice.lower() in ("sh", "5"):
                    remove_resource(player, [1,4])
                else:
                    remove_resource(player, [buildingchoice])
            elif choice == 2: #trade
                trade(input("Enter player 1: "), input("Enter player 2: "), get_numbers(input("Enter resources 1 (1:wood 2:stone 3:wheet 4:sheep 5:ore): ")), get_numbers(input("Enter resources 2 (1:wood 2:stone 3:wheet 4:sheep 5:ore): ")))
            elif choice == 3: #Steal
                victim = input("Enter victim: ")
                if victim == "q":
                    continue
                else:
                    card = input("Enter card (1:wood 2:stone 3:wheet 4:sheep 5:ore): ")
                    remove_resource(victim, [card])
            elif choice == 4: #split
                player_a = input("Enter amount of players: ")
                if player_a == "q":
                    continue
                else:
                    for i in range(int(player_a)):
                        remove_resource(input("Enter player name: "), get_numbers(input("Enter resources (1:wood 2:stone 3:wheet 4:sheep 5:ore): ")))
            elif choice == 5: #add source
                source_a = input("Enter amount of sources: ")
                if source_a == "q":
                    continue
                else:
                    source_a = int(source_a)
                    for i in range(source_a):
                        add_source(player, int(input(f"Enter source ({i+1}/{source_a}) number (2-12): ")), int(input("Enter resource (1:wood 2:stone 3:wheet 4:sheep 5:ore 6:custom): ")))
            elif choice == 6: #add resources
                add_resource(player, get_numbers(input("Enter resources (1-6): ")))
            elif choice == 7: #remove latest source
                players[player]["sources"].popitem()
            elif choice == 8: #next turn
                roll = input("Enter roll (2-12): ")
                if roll == "q":
                    continue
                else:
                    new_roll(player, roll)
                    turn += 1
                    nextturn = 1
            elif choice == 9: #input custom data
                data = input("Enter full data (The data must me in the correct format):")
                if data == "q":
                    continue
                else:
                    players = json.loads(data)
            else:
                print("Invalid choice.")
            time.sleep(0.5)

def init_game():
    print("""╔═╗╔═╗╔╦╗╔═╗╔╗╔  ┌┬┐┬─┐┌─┐┌─┐┬┌─┌─┐┬─┐  
║  ╠═╣ ║ ╠═╣║║║   │ ├┬┘├─┤│  ├┴┐├┤ ├┬┘  
╚═╝╩ ╩ ╩ ╩ ╩╝╚╝   ┴ ┴└─┴ ┴└─┘┴ ┴└─┘┴└─  V2.0
──────────────────────────────────────
A simple irl Settlers of Catan card and player tracker. (With the seafarers gold resource)\n""")
    amount_of_players = int(input("Enter the amount of players: "))
    for i in range(amount_of_players):
        name = input(f"Enter player name ({i+1}/{amount_of_players}): ")
        add_player(name)
    



init_game()
main()