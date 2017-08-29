import json
from app.helpers.dealHandler import DealHandler
import requests
import time

"""
cards_on_the_table_filename = "json/deal.json"
only_cards = []
with open(cards_on_the_table_filename) as file:
    for line in file:
        lines = [line] + list(itertools.islice(file, 2))
        cards_on_the_table = json.loads(''.join(lines))
        only_cards.append(cards_on_the_table["cards_played"])
deal = DealHandler(distribution, contract, only_cards)
deal.start_deal()
print(deal.tricks)
"""

distribution_filename = "app/helpers/json/distribution.json"
with open(distribution_filename) as file:
    distribution = json.load(file)
contract = "2SE"

deal = DealHandler(distribution, contract, [])
while True:
    snapshots = requests.get("http://127.0.0.1:5000/snapshots/lasts").json()
    print(snapshots)
    deal.get_cards_every_second(snapshots["snapshots"][0]["cards_played"], snapshots["snapshots"][1]["cards_played"])
    print(deal.tricks)
    tricks_json = {"tricks": deal.tricks, "board": 1, "table": 1, "trick_index": deal.current_trick_index}
    headers = {'Content-type': 'application/json'}
    print(tricks_json)
    r = requests.post("http://127.0.0.1:5000/tricks", data=json.dumps(tricks_json), headers=headers)
    print(r.content)
    print("trick index: {}".format(deal.current_trick_index))
    for player in deal.players:
        print(player)
        print(deal.tricks[player][deal.current_trick_index-1])
    time.sleep(2)
    if deal.current_trick_index == 13:
        break
for i in range(13):
    for player in deal.players:
        print("trick {}: {} {}".format(i+1, player, deal.tricks[player][i]))
