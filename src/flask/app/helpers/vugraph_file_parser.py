import json

filename = "vugraph.lin"
with open(filename) as file:
    data = file.readlines()

boards = data[3:]

distribution = {"o": {}, "c": {}}
colors = ['S', 'H', 'D', 'C']
players = ['N', 'E', 'S', 'W']
for i, board in enumerate(boards):
    boards_splited = board.split("|")
    board_id = boards_splited[1]
    room_id = board_id[0]
    board_number = board_id[1:]
    distribution[room_id][board_number] = [{}, {}]
    board_distribution = boards_splited[5]
    board_distribution_splited = board_distribution.split(",")
    hand = []
    distribution[room_id][board_number][1]["vulnerability"] = boards_splited[7]
    for j, suit in enumerate(board_distribution_splited):
        if suit[0] != "S":
            dealer = int(suit[0])
            distribution[room_id][board_number][1]["dealer"] = players[dealer-1]
            suit = suit[1:]
        hand = []
        for k, color in enumerate(colors):
            if color == "C":
                row = [l + color for l in suit[suit.index(color) + 1:]]
            else:
                row = [l + color for l in suit[suit.index(color) + 1:suit.index(colors[k+1])]]
            hand += row
        distribution[room_id][board_number][0][players[j]] = hand

# print(distribution)

with open("json/distribution_{}.json".format(filename), "w") as f:
    json.dump(distribution, f)
