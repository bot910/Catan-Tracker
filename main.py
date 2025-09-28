from collections import Counter #counter for counting resources
from typing import Literal #type hinting for literals
import time #time for sleep
import sys #sys for clearing console
import ast #ast for parsing a python dict
import os #os for clearing console

players = {}
blocked_s = ""
nextprint = ""

def clear(): #clear console
    if sys.platform.startswith("win"):
        os.system("cls")
    else:
        os.system("clear")

def get_numbers(input: str): #get list of numbers from input
    user_input = input
    if not user_input:
        return []
    else:
        numbers = [int(num.strip()) for num in user_input.split(",")]
        return numbers

def num_to_resource(num: int): #convert number to resource name
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

def get_amount_of_resources(name: str, resource: int): #get amount of specific resource a player has
    global players
    resources = players[name].get("resources", [])

    if resource is None:
        return 0
    else:
        return resources.count(int(resource))

def add_blocked_source(name: str, number: int, resource: int, amount: int): #add blocked source to player
    global players
    if resource > 0 and resource < 7 and number > 1 and number < 13 and name in players:
        if "blocked" not in players[name]:
            players[name]["blocked"] = []
        players[name]["blocked"].append((number, resource, amount))

def remove_all_blocked_sources(): #remove all blocked sources from players
    global players
    for name in players:
        if "blocked" in players[name]:
            del players[name]["blocked"]

def add_player(name: str): #add player to game
    global players
    players[name] = {"order":len(players)+1}

def get_player_order(order: int): #get player name by order
    global players
    for name, info in players.items():
        if info.get("order") == order:
            return name
    return None

def get_player_resources(name: str): #get list of resources a player has
    global players
    if name not in players:
        raise ValueError(f"Player {name} does not exist.")
    elif "resources" not in players[name]:
        return []
    else:
        return players[name]["resources"]

def format_resources(name: str, resources: list): #format resources for printing
    global players
    counts = Counter(resources)
    formatted = " ".join(f"{num}:{num_to_resource(num)} = {counts[num]}," for num in sorted(counts))
    return f"{name}: {formatted}"

def add_resource(name: str, resources: list, dontshow=False): #add resources to player
    global players
    global nextprint
    processed = []
    for r in resources:
        if r > 6 or r < 1:
            print(f"Invalid resource {r}. Skipping.")
        elif r == 6:
            choice = input(f"Resource '(6) gold' for {name} detected! Enter choice: ")
            if not choice or choice == 6:
                print("No valid choice made. Skipping.")
            processed.append(int(choice))
        else:
            processed.append(r)

    if "resources" not in players[name]:
        players[name]["resources"] = processed.copy()
    else:
        players[name]["resources"].extend(processed)
    if not dontshow:
        nextprint += f"Added {processed} to {name}\n"

def remove_resource(name: str, resource: list): #remove resources from player
    global players
    if name not in players:
        print(f"Player {name} does not exist.")
    elif "resources" not in players[name]:
        print(f"Player {name} has no resources.")
    else:
        for r in resource:
            if r > 0 and r < 7:
                if r not in players[name]["resources"]:
                    print(f"{name} does not have resource {r}. Skipping.")
                else:
                    players[name]["resources"].remove(r)
            else:
                print(f"Invalid resource {r}.")
            
def trade(name1: str, name2: str, resource1: list, resource2: list): #trade resources between players
    global players
    global nextprint
    try:
        name1 = int(name1)
    except ValueError:
        pass
    try:
        name2 = int(name2)
    except ValueError:
        pass
    if type(name1) == int and type(name2) == int:
        name1 = get_player_order(name1)
        name2 = get_player_order(name2)
    if name1 not in players or name2 not in players:
        print("Player does not exist.")
        return
    if resource1 == [] or resource2 == []:
        print("No resources specified.")
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
    nextprint += f"Traded {resource1} from {name1} to {name2} for {resource2}\n"
    add_resource(name1, resource2, dontshow=True)
    remove_resource(name2, resource2)
    add_resource(name2, resource1, dontshow=True)
    remove_resource(name1, resource1)

def add_source(name: str, number: Literal[2,3,4,5,6,7,8,9,10,11,12], resource: Literal[1,2,3,4,5,6]): #add resource source to player
    global players
    if resource > 0 and resource < 7 and number > 1 and number < 13 and name in players:
        if "sources" not in players[name]:
            players[name]["sources"] = {}

        if number not in players[name]["sources"]:
            players[name]["sources"][number] = []

        players[name]["sources"][number].append(resource)

def new_roll(p, number): #process new roll and add resources to players
    global players
    global nextprint
    number = int(number)
    nextprint = ""
    for name, data in players.items():
        sources = data.get("sources", {})
        blocked = data.get("blocked", [])
        if number in sources:
            resources = sources[number].copy()
            blocked_counts = {}
            for b in blocked:
                b_num, b_res, b_amt = b
                if b_num == number:
                    blocked_counts[b_res] = blocked_counts.get(b_res, 0) + b_amt
            unblocked_resources = []
            res_counter = Counter(resources)
            for res, count in res_counter.items():
                blocked_amt = blocked_counts.get(res, 0)
                allowed = max(0, count - blocked_amt)
                unblocked_resources.extend([res] * allowed)
            if unblocked_resources:
                add_resource(name, unblocked_resources, dontshow=True)
                names_to_add = [num_to_resource(r) for r in unblocked_resources]
                nextprint += f"Added {unblocked_resources}:{names_to_add} to {name} for roll {number}\n"
            else:
                nextprint += f"No resources added to {name} for roll {number} (all sources blocked)\n"

def main(): #main game loop
    global blocked_s
    global players
    global nextprint
    turn = 1
    while True:
        nextturn = 0
        while nextturn == 0:
            clear()
            print(nextprint)
            print(f"\nBlocked source: {blocked_s}")
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
    5 - Play action card
    6 - Add source
    7 - Add resources
    8 - Next turn
    9 - Advanced options\n""")
            
            print("Debug (full list of players and data):")
            print(players)

            choice = input("Enter choice (1-9): ").strip()
            try:
                choice = int(choice)
            except ValueError:
                print("Invalid choice. Please try again.")
                time.sleep(0.75)
                continue

            if choice == 1: #build
                buildingchoice = input("Enter building (VI, CI, CA, ST, SH or 1-5): ")
                if buildingchoice == "q" or buildingchoice == "":
                    continue
                elif buildingchoice.lower() in ("vi", "1"):
                    cost = input("Chooste resources to use, leave blank to use default (1:wood 2:stone 3:wheet 4:sheep 5:ore): ")
                    if not cost == "q":
                        if cost == "":
                            cost_t = [1,2,3,4]
                        else:
                            cost_t = get_numbers(cost)
                        nextprint += f"{player} built a village using {cost_t}.\n"
                        remove_resource(player, cost_t)
                elif buildingchoice.lower() in ("ci", "2"):
                    cost = input("Chooste resources to use, leave blank to use default (1:wood 2:stone 3:wheet 4:sheep 5:ore): ")
                    if not cost == "q":
                        if cost == "":
                            cost_t = [3,3,5,5,5]
                        else:
                            cost_t = get_numbers(cost)
                        nextprint += f"{player} built a city using {cost_t}.\n"
                        remove_resource(player, cost_t)
                elif buildingchoice.lower() in ("ca", "3"):
                    cost = input("Chooste resources to use, leave blank to use default (1:wood 2:stone 3:wheet 4:sheep 5:ore): ")
                    if not cost == "q":
                        if cost == "":
                            cost_t = [3,4,5]
                        else:
                            cost_t = get_numbers(cost)
                        nextprint += f"{player} bought a card using {cost_t}.\n"
                        remove_resource(player, cost_t)
                elif buildingchoice.lower() in ("st", "4"):
                    cost = input("Chooste resources to use, leave blank to use default (1:wood 2:stone 3:wheet 4:sheep 5:ore): ")
                    if not cost == "q":
                        if cost == "":
                            cost_t = [1,2]
                        else:
                            cost_t = get_numbers(cost)
                        nextprint += f"{player} built a street using {cost_t}.\n"
                        remove_resource(player, cost_t)
                elif buildingchoice.lower() in ("sh", "5"):
                    cost = input("Chooste resources to use, leave blank to use default (1:wood 2:stone 3:wheet 4:sheep 5:ore): ")
                    if not cost == "q":
                        if cost == "":
                            cost_t = [1,4]
                        else:
                            cost_t = get_numbers(cost)
                        nextprint += f"{player} built a ship using {cost_t}.\n"
                        remove_resource(player, cost_t)
                else:
                    continue

            elif choice == 2: #trade
                trade(input("Enter player 1: "), input("Enter player 2: "), get_numbers(input("Enter resources 1 (1:wood 2:stone 3:wheet 4:sheep 5:ore): ")), get_numbers(input("Enter resources 2 (1:wood 2:stone 3:wheet 4:sheep 5:ore): ")))
            
            elif choice == 3: #Steal
                victim = input("Enter victim: ")
                if victim == "q" or victim == "":
                    continue
                else:
                    card = input("Enter card (1:wood 2:stone 3:wheet 4:sheep 5:ore): ")
                    if not card == "q" or card == "":
                        card = int(card)
                        if get_amount_of_resources(victim, card) == 0:
                            continue
                        nextprint += f"{player} stole {card}:{num_to_resource(card)} from {victim}.\n"
                        add_resource(player, [card], dontshow=True)
                        remove_resource(victim, [card])
            
            elif choice == 4: #split
                player_a = input("Enter amount of players: ")
                if player_a == "q" or player_a == "":
                    continue
                else:
                    for i in range(int(player_a)):
                        player_n = input(f"Enter player name ({i+1}/{player_a}): ")
                        if not player_n == "q" or player_n == "":
                            try:
                                player_n = int(player_n)
                            except ValueError:
                                pass
                            if type(player_n) == int:
                                player_n = get_player_order(player_n)
                            res = get_numbers(input("Enter resources (1:wood 2:stone 3:wheet 4:sheep 5:ore): "))
                            remove_resource(player_n, res)
                            nextprint += f"{player_n} lost resources {res}.\n"
            
            elif choice == 5: #play action card
                card_a = input("Enter card (1:mon,2:inv): ")
                if card_a == "q" or card_a == "":
                    continue
                elif card_a in ("1", "mon", "mo", "monopoly"): 
                    card_chosen = input("Enter card (1:wood 2:stone 3:wheet 4:sheep 5:ore): ")
                    total_amount = 0
                    for name in players:
                        amount_of_card_chosen = get_amount_of_resources(name,int(card_chosen))
                        total_amount += amount_of_card_chosen
                        for i in range(amount_of_card_chosen):
                            remove_resource(name, [int(card_chosen)])
                    total_amount -= get_amount_of_resources(player, int(card_chosen))
                    add_resource(player, [int(card_chosen)] * total_amount, dontshow=True)
                    nextprint += f"{player} played monopoly for {num_to_resource(int(card_chosen))}, taking {total_amount} {num_to_resource(int(card_chosen))} from all players.\n"
                    
                elif card_a in ("2", "inv", "in", "invention"):
                    player_name = input("Enter player name: ")
                    add_resource(player_name, input("Enter resources (1:wood 2:stone 3:wheet 4:sheep 5:ore): "))
                    add_resource(player_name, input("Enter resources (1:wood 2:stone 3:wheet 4:sheep 5:ore): "))
            
            elif choice == 6: #add source
                source_a = input("Enter amount of sources: ")
                if source_a == "q" or source_a == "":
                    continue
                else:
                    source_a = int(source_a)
                    for i in range(source_a):
                        source_n = str(input(f"Enter source ({i+1}/{source_a}) number (2-12): "))
                        if source_n == "q" or source_n == "":
                            continue
                        source_r = str(input("Enter resource (1:wood 2:stone 3:wheet 4:sheep 5:ore 6:custom): "))
                        if source_r == "q" or source_r == "":
                            continue
                        else:
                            source_n = int(source_n)
                            for i in range(len(source_r)):
                                if source_r[i] == ",":
                                    pass
                                else:
                                    add_source(player, source_n, int(source_r[i]))
            
            elif choice == 7: #add resources
                add_resource(player, get_numbers(input("Enter resources (1:wood 2:stone 3:wheet 4:sheep 5:ore): ")))
            
            elif choice == 8: #next turn
                roll = input("Enter roll (2-12): ")
                if roll == "q" or roll == "":
                    continue
                else:
                    new_roll(player, roll)
                    turn += 1
                    nextturn = 1

            elif choice == 9: #input custom data
                clear()
                if turn == 1:
                    player = get_player_order(1)
                    print("Starting player:", player)
                else:
                    player = get_player_order((turn - 1) % len(players) + 1)
                    print("Current player:", player)

                for name in players:
                    print(format_resources(name, get_player_resources(name)))
                print("""\nAdvanced options:
    1. Remove resources
    2. Remove latest source
    3. Import full data (Python dict format)
    4. Switch player (without rolling) 
    5. Set the current blocked source for players (by the bandit)\n""")
                print("Debug (full list of players and data):")
                print(players)
                choice_a = input("\nEnter choice (1-4): ").strip()
                if choice_a == "q" or choice_a == "":
                    continue
                elif choice_a == "1":
                    remove_resource(player, get_numbers(input("Enter resources (1:wood 2:stone 3:wheet 4:sheep 5:ore): ")))
                elif choice_a == "2": #remove latest source
                    if "sources" not in players[player] or len(players[player]["sources"]) == 0:
                        print("No sources to remove.")
                    else:
                        players[player]["sources"].popitem()
                elif choice_a == "3":
                    data = input("Enter full data (The data must me in the correct format):")
                    if data == "q" or data == "":
                        continue
                    else:
                        try:
                            parsed = ast.literal_eval(data)
                            if not isinstance(parsed, dict):
                                print("Parsed value is not a dict.")
                            else:
                                players = parsed
                                print("Imported data successfully.\n")
                                print(f"Players are now: {players.keys()}")
                                time.sleep(0.75)
                        except Exception as e:
                            print("Failed to parse input as Python literal:", e)
            
                elif choice_a == "4":
                    choice_p = input("Enter the amount of turns to advance: ")
                    if choice_p == "q" or choice_p == "":
                        continue
                    else:
                        try:
                            choice_p = int(choice_p)
                            if choice_p < 1:
                                print("Invalid amount of turns.")
                            else:
                                turn += choice_p
                                nextturn = 1
                        except ValueError:
                            print("Invalid input.")
                elif choice_a == "5":
                    blocked_r = input("Enter blocked source and resource (1-12:1-6): ")
                    blocked_s = blocked_r
                    if blocked_r == "q":
                        continue
                    elif blocked_r == "":
                        remove_all_blocked_sources()
                        nextprint += "Removed all blocked source.\n"
                    else:
                        remove_all_blocked_sources()
                        blocked_r = blocked_r.split(":")
                        blocked_rs = blocked_r[0]
                        blocked_r = blocked_r[1]
                        blocked_a = input("Enter amount of players: ")
                        if blocked_a == "q" or blocked_a == "":
                            continue
                        else:
                            for i in range(int(blocked_a)):
                                blocked_n = input(f"Enter player name or number ({i+1}/{blocked_a}) and amount of sources to block (name:amount): ")
                                if blocked_n == "q" or blocked_n == "":
                                    continue
                                else:
                                    blocked_n = blocked_n.split(":")
                                    blocked_ns = blocked_n[0]
                                    blocked_na = int(blocked_n[1])
                                    try:
                                        blocked_ns = int(blocked_ns)
                                    except ValueError:
                                        pass
                                    if type(blocked_ns) == int:
                                        blocked_ns = get_player_order(blocked_ns)
                                    add_blocked_source(blocked_ns, int(blocked_rs), int(blocked_r), blocked_na)
                        nextprint += f"Set blocked source {blocked_rs}:{num_to_resource(int(blocked_r))} for {blocked_a} players.\n"

                    
            else:
                print("Invalid choice. Please try again.")
            
            time.sleep(0.75)

def init_game(): #initialize game and players
    print("""╔═╗╔═╗╔╦╗╔═╗╔╗╔  ┌┬┐┬─┐┌─┐┌─┐┬┌─┌─┐┬─┐  
║  ╠═╣ ║ ╠═╣║║║   │ ├┬┘├─┤│  ├┴┐├┤ ├┬┘  
╚═╝╩ ╩ ╩ ╩ ╩╝╚╝   ┴ ┴└─┴ ┴└─┘┴ ┴└─┘┴└─  V3.0
──────────────────────────────────────
A simple irl Settlers of Catan card and player tracker. (With the seafarers gold resource)\n""")
    amount_of_players = int(input("Enter the amount of players: "))
    for i in range(amount_of_players):
        name = input(f"Enter player name ({i+1}/{amount_of_players}): ")
        add_player(name)
    
init_game()
main()
