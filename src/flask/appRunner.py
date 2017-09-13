import json
from app.helpers.dealHandler import DealHandler
import requests
import time

distribution_filename = "app/helpers/json/distribution.json"
distribution_filename = "app/helpers/json/distribution_vugraph.lin.json"
contract = "2SE"
with open(distribution_filename) as file:
    # distribution = json.load(file)
    # print(file.read())
    distribution_segment = json.load(file)

# room = "c"
room = "o"
table_id = 1
segment_length = len(distribution_segment[room])
for board_id in range(1, len(distribution_segment[room])+1):
    board_id = str(board_id)
    distribution = distribution_segment[room][board_id][0]
    deal = DealHandler(distribution, contract)

    while True:
        if not deal.error:
            deal.current_snapshot_index += 1
            print(deal.current_snapshot_index)
            snapshots = requests.get("http://127.0.0.1:5000/snapshots/{}".format(deal.current_snapshot_index))
            if snapshots.status_code == 200:
                snapshots = snapshots.json()
                if len(snapshots["snapshots"]) < 2:
                    time.sleep(2)
                    continue
                else:
                    deal.get_cards_every_second(snapshots["snapshots"][0]["cards_played"],
                                                snapshots["snapshots"][1]["cards_played"])
                    tricks_json = {
                        "tricks": deal.tricks,
                        "board": board_id,
                        "table": table_id,
                        "trick_index": deal.current_trick_index
                    }
                    headers = {'Content-type': 'application/json'}
                    r = requests.post("http://127.0.0.1:5000/tricks", data=json.dumps(tricks_json), headers=headers)
                    time.sleep(2)
                    if deal.current_trick_index == 13:
                        break
            else:
                deal.current_snapshot_index -= 1
                time.sleep(1)
                continue
        else:
            print(deal.error_message)
            tricks_from_user = input("Put deal.tricks here. Actual value = {} ".format(deal.tricks))
            deal.tricks = json.loads(tricks_from_user)
            deal.error = 0
        print("Current trick: {}".format(deal.current_trick))

    for i in range(13):
        for player in deal.players:
            print("trick {}: {} {}".format(i+1, player, deal.tricks[player][i]))
