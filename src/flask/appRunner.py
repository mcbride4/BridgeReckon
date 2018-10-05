import json
from app.helpers.dealHandler import DealHandler
import requests
import time
import random
from pymongo import MongoClient


distribution_filename = "app/helpers/json/distribution.json"
distribution_filename = "app/helpers/json/distribution_vugraph.lin.json"
contract = "2HE"
with open(distribution_filename) as file:
    # distribution = json.load(file)
    # print(file.read())
    distribution_segment = json.load(file)


client = MongoClient('localhost', 27017)
db = client.bridge
snapshots = db.snapshots
errorsolutions = db.errorsolutions
errorsolutions.drop()
db.errors.drop()
db.tricks.drop()
# room = "c"
room = "c"
table_id = 1
raspberry_id = 1
segment_length = len(distribution_segment[room])
print("segment length: {}".format(segment_length))
current_snapshot_index_segment = 0
tricks_json_previous = {}
err = 0
previous_snapshot_index = 0

for board_id in range(1, segment_length+1):
    print("starting new board!! Board number: {} of {}".format(board_id, segment_length))
    board_id = str(board_id)
    distribution = distribution_segment[room][board_id][0]
    deal = DealHandler(distribution, contract)
    deal.current_snapshot_index = current_snapshot_index_segment
    deal.paths['1'] = ''
    deal.paths['2'] = ''
    deal.paths['3'] = ''
    deal.paths['4'] = ''
    while True:
        # time.sleep(2)
        if not deal.error:
            if deal.current_snapshot_index < snapshots.find({'raspberry_id': raspberry_id}).count() // 2 - 1:
                deal.current_snapshot_index += 1
                r = requests.get("http://127.0.0.1:5000/snapshots/{}/{}".format(
                    raspberry_id, deal.current_snapshot_index))
                if r.status_code == 200:
                    print("deal current snapshot index: {}".format(deal.current_snapshot_index))
                    last_two_snapshots = r.json()
                    if not last_two_snapshots["snapshots"][0] or not last_two_snapshots["snapshots"][1]:
                        # time.sleep(5)
                        continue
                    else:
                        print("last two snapshots: \n{}".format(last_two_snapshots["snapshots"]))
                        if last_two_snapshots["snapshots"][0]["camera_id"] == 1:
                            deal.paths['1'] = last_two_snapshots["snapshots"][0]['path']
                            deal.paths['2'] = last_two_snapshots["snapshots"][1]['path']
                        if last_two_snapshots["snapshots"][0]["camera_id"] == 2:
                            deal.paths['3'] = last_two_snapshots["snapshots"][0]['path']
                            deal.paths['4'] = last_two_snapshots["snapshots"][1]['path']

                        deal.get_cards_every_second(last_two_snapshots["snapshots"][0]["cards"],
                                                    last_two_snapshots["snapshots"][1]["cards"])
                        tricks_json = {
                            "tricks": deal.tricks,
                            "board": board_id,
                            "table": table_id,
                            "trick_index": deal.current_trick_index
                        }
                        if tricks_json != tricks_json_previous and not deal.error:
                            print("now i'll send post request")
                            headers = {'Content-type': 'application/json'}
                            tricks_json_previous = tricks_json.copy()
                            r = requests.post("http://127.0.0.1:5000/tricks", data=json.dumps(tricks_json), headers=headers)
                            # time.sleep(5)
                            if deal.current_trick_index == 13:
                                print("breaking the loop beacause 13 tricks: {}".format(deal.current_trick_index))
                                break
                        else:
                            print("i'm NOT sending any request!!!")
                        # time.sleep(5)
                    r.close()
                else:
                    # deal.current_snapshot_index -= 1
                    # time.sleep(5)
                    previous_snapshot_index = deal.current_trick_index.copy()
                    continue
        else:
            uid = random.getrandbits(32)
            err += 1
            possible_tricks = deal.tricks.copy()
            for key in deal.tricks.keys():
                possible_tricks[key][deal.current_trick_index] = deal.current_trick[key]
            errors_json = {
                "errors": deal.error_message,
                "board": board_id,
                "table": table_id,
                "uid": uid,
                "tricks": possible_tricks,
                'path1': deal.paths['1'],
                'path2': deal.paths['2'],
                'path3': deal.paths['3'],
                'path4': deal.paths['4'],
            }
            r = requests.post("http://127.0.0.1:5000/errors", data=json.dumps(errors_json), headers=headers)
            print(deal.error_message)
            r.close()
            while True:
                # if err <= errorsolutions.count():
                #     print(uid)
                    r = requests.get("http://127.0.0.1:5000/errorsolutions/{}".format(uid), headers=headers)
                    # print(r.content, uid)
                    # print(r.status_code)
                    if r.status_code == 200:

                        tricks_from_user = json.loads(r.json()['errorsolutions']['errorsolution'][0])
                        for key, value in tricks_from_user.items():
                            tricks_from_user[key] = value[1:-1].replace("\"", '').split(',')
                        deal.tricks = tricks_from_user
                        curr_trick = {}
                        for key in tricks_from_user.keys():
                            curr_trick[key] = tricks_from_user[key][deal.current_trick_index]

                        was = False
                        for previous_trick in deal.previous_tricks:
                            if len(previous_trick.items() & curr_trick.items()) == 4:
                                was = True

                        if (not was) and ('' not in curr_trick):
                            deal.current_trick = curr_trick
                            deal.close_trick()
                            tricks_json = {
                                "tricks": deal.tricks,
                                "board": board_id,
                                "table": table_id,
                                "trick_index": deal.current_trick_index
                            }
                            tricks_json_previous = tricks_json.copy()
                            r = requests.post("http://127.0.0.1:5000/tricks", data=json.dumps(tricks_json), headers=headers)
                            deal.current_trick = {"N": "", "E": "", "S": "", "W": ""}
                            curr_trick = {"N": "", "E": "", "S": "", "W": ""}
                        else:
                            deal.current_trick = curr_trick
                            # deal.current_trick_index += -1
                            tricks_json = {
                                "tricks": tricks_from_user,
                                "board": board_id,
                                "table": table_id,
                                "trick_index": deal.current_trick_index
                            }
                        break


            deal.error = 0
            r.close()
        if deal.current_trick_index != previous_snapshot_index:
            print("Current trick: {}".format(deal.current_trick))
            print("Next trick: {}".format(deal.next_trick_candidates))

    current_snapshot_index_segment = deal.current_snapshot_index
    for i in range(13):
        for player in deal.players:
            print("trick {}: {} {}".format(i+1, player, deal.tricks[player][i]))
