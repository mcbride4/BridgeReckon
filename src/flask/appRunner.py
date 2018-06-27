import json
from app.helpers.dealHandler import DealHandler
import requests
import time
import random

distribution_filename = "app/helpers/json/distribution.json"
distribution_filename = "app/helpers/json/distribution_vugraph.lin.json"
contract = "2HE"
with open(distribution_filename) as file:
    # distribution = json.load(file)
    # print(file.read())
    distribution_segment = json.load(file)

# room = "c"
room = "c"
table_id = 1
raspberry_id = 101
segment_length = len(distribution_segment[room])
print("segment length: {}".format(segment_length))
current_snapshot_index_segment = 0
tricks_json_previous = {}

for board_id in range(1, segment_length+1):
    print("starting new board!! Board number: {} of {}".format(board_id, segment_length))
    board_id = str(board_id)
    distribution = distribution_segment[room][board_id][0]
    deal = DealHandler(distribution, contract)
    deal.current_snapshot_index = current_snapshot_index_segment
    while True:
        if not deal.error:
            deal.current_snapshot_index += 1
            print("deal current snapshot index: {}".format(deal.current_snapshot_index))
            last_two_snapshots = requests.get("http://127.0.0.1:5000/snapshots/{}/{}".format(
                raspberry_id, deal.current_snapshot_index))
            if last_two_snapshots.status_code == 200:
                last_two_snapshots = last_two_snapshots.json()
                if not last_two_snapshots["snapshots"][0] or not last_two_snapshots["snapshots"][1]:
                    time.sleep(0.2)
                    continue
                else:
                    print("last two snapshots: \n{}".format(last_two_snapshots["snapshots"]))
                    deal.get_cards_every_second(last_two_snapshots["snapshots"][0]["cards"],
                                                last_two_snapshots["snapshots"][1]["cards"])
                    tricks_json = {
                        "tricks": deal.tricks,
                        "board": board_id,
                        "table": table_id,
                        "trick_index": deal.current_trick_index
                    }
                    if tricks_json != tricks_json_previous:
                        print("now i'll send post request")
                        headers = {'Content-type': 'application/json'}
                        tricks_json_previous = tricks_json.copy()
                        r = requests.post("http://127.0.0.1:5000/tricks", data=json.dumps(tricks_json), headers=headers)

                        if deal.current_trick_index == 13:
                            print("breaking the loop beacause 13 tricks: {}".format(deal.current_trick_index))
                            break
                    else:
                        print("i'm NOT sending any request!!!")
                    time.sleep(0.2)
            else:
                deal.current_snapshot_index -= 1
                time.sleep(0.2)
                continue
        else:
            uid = random.getrandbits(32)
            errors_json = {
                "errors": deal.error_message,
                "board": board_id,
                "table": table_id,
                "uid": uid,
                "tricks": deal.tricks
            }
            r = requests.post("http://127.0.0.1:5000/errors", data=json.dumps(errors_json), headers=headers)
            print(deal.error_message)
            while True:
                time.sleep(1)
                r = requests.get("http://127.0.0.1:5000/errorSolution/{}".format(uid), headers=headers)
                print(r.json())
                if r.status_code == 200:
                    tricks_from_user = r.json()['tricks']
                    deal.tricks = json.loads(tricks_from_user)
                    break

            deal.error = 0
        print("Current trick: {}".format(deal.current_trick))
        print("Next trick: {}".format(deal.next_trick_candidates))

    current_snapshot_index_segment = deal.current_snapshot_index
    for i in range(13):
        for player in deal.players:
            print("trick {}: {} {}".format(i+1, player, deal.tricks[player][i]))
