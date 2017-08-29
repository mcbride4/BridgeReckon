import json
import itertools
import time


class DealHandler(object):
    def __init__(self, distribution, contract, cards_on_the_table):
        self.players_order = ["N", "E", "S", "W", "N", "E", "S", "W"]
        self.players = ["N", "E", "S", "W"]
        self.distribution = distribution
        self.cards_played = {"N": [], "S": [], "E": [], "W": []}
        self.cards_candidates = {"N": [], "S": [], "E": [], "W": []}
        self.cards_unplayed = dict(distribution)
        self.contract = contract
        self.tricks_taken = {"N": 0, "S": 0, "E": 0, "W": 0}
        self.cards_seen_on_the_table = cards_on_the_table  # to co przychodzi co 2 sekundy spakowane do jednego slownika.
        self.current_snapshot_index = 0
        self.cards_snapshot_last = []
        self.cards_snapshot_last_but_one = []
        self.tricks = {"N": ["", "", "", "", "", "", "", "", "", "", "", "", ""],
                       "S": ["", "", "", "", "", "", "", "", "", "", "", "", ""],
                       "E": ["", "", "", "", "", "", "", "", "", "", "", "", ""],
                       "W": ["", "", "", "", "", "", "", "", "", "", "", "", ""]}
        """ tu mniej wiecej taki format: {
        N: ["2H", "2S", ...],
        S: ["5H", "AS", ...],
        E: ["6H", "KS", ...],
        W: ["7H", "3S", ...]
        } indeks to nr lewy-1
        """
        self.last_trick_winner = ""
        self.tricks_starting_players = []  # ["N", "W", ...] # indeks to nr lewy-1
        self.declarer = self.resolve_declarer()
        self.dummy = self.resolve_dummy()
        self.trick_orders = self.set_trick_orders()
        self.tricks_in_order = {}
        self.current_trick_index = 0
        self.current_trick = {"N": "", "E": "", "S": "", "W": ""}
        self.next_trick_candidates = {"N": "", "E": "", "S": "", "W": ""}

    def move_card_to_candidates(self, card):
        # self.
        pass

    def resolve_declarer(self):
        return self.contract[2]

    def resolve_dummy(self):
        return self.players_order[self.players_order.index(self.declarer) + 2]

    def resolve_first_lead_player():
        return self.players_order[self.players_order.index(self.declarer) + 1]

    def init_cards_unplayed():
        # or mayby it can be done in __init__ ?
        pass

    def move_card_to_played(self):
        pass

    def set_last_trick_winner():
        pass

    def read_next_postiiton_on_the_table(self):
        # cards_showed_up = [set(self.cards_snapshot_last) - set(self.cards_snapshot_last_but_one)]
        # cards_hided = [set(self.cards_snapshot_last_but_one) - set(self.cards_snapshot_last)]
        cards_showed_up = [x for x in set(self.cards_snapshot_last) if x not in set(self.cards_snapshot_last_but_one)]
        cards_hided = [x for x in set(self.cards_snapshot_last_but_one) if x not in set(self.cards_snapshot_last)]
        # print("snapshots: ")
        # print("{}".format(self.cards_snapshot_last))
        # print("{}".format(self.cards_snapshot_last_but_one))
        print("cards showed up: {}".format(cards_showed_up))
        print("cards hidded: {}".format(cards_hided))
        if cards_hided:
            self.on_cards_hided(cards_hided)
        if cards_showed_up:
            self.on_cards_showed_up(cards_showed_up)

    def on_cards_showed_up(self, cards_showed_up):
        dummies_cards = []
        other_cards = []
        for card in cards_showed_up:
            if self.card_is_dummys(card):
                dummies_cards.append(card)
            else:
                other_cards.append(card)
        for card in other_cards:

            added = self.add_to_trick(card)
            if added:
                if self.current_trick_length() == 4:
                    self.move_current_trick_to_played()
                    self.move_next_trick_to_current()
            else:
                added_next = self.add_to_next_trick(card)
            # if added_next:

            # move_card_to_candidates(card)
        for card in dummies_cards:
            # move_card_to_candidates(card) # to trzeba jeszcze przemyslec. czy np dummy nie powinien miec innych kandydatow niz cala reszta
            pass

    def on_cards_hided(self, cards_hided):
        dummies_cards = []
        other_cards = []
        for card in cards_hided:
            if self.card_is_dummys(card):
                dummies_cards.append(card)
            else:
                other_cards.append(card)
        for card in other_cards:
            # self.move_card_to_played(card)
            pass
        if len(dummies_cards) > 2:
            print("ERROR !!! DON'T KNOW WHAT TO DO!")
            return
        for card in dummies_cards:
            if self.add_to_trick(card):
                self.close_trick()
            else:
                self.add_to_next_trick(card)

        # changes between last and last_but_one positions on the table
        pass

    def close_trick(self):
        if self.current_trick_length() == 4:
            self.move_current_trick_to_played()
            self.move_next_trick_to_current()
            self.current_trick_index += 1

    def move_current_trick_to_played(self):
        for key, value in self.current_trick.items():
            self.tricks[key][self.current_trick_index] = value

    def move_next_trick_to_current(self):
        for key, value in self.next_trick_candidates.items():
            self.current_trick[key] = value

    def current_trick_length(self):
        counter = 0
        for key, value in self.current_trick.items():
            if value:
                counter += 1
        return counter

    def add_to_trick(self, card):
        owner = self.find_card_owner(card)
        if self.validate_addition(owner):
            self.current_trick[owner] = card
            return True
        return False

    def add_to_next_trick(self, card):
        owner = self.find_card_owner(card)
        if self.validate_addition(owner, "next"):
            self.next_trick_candidates[owner] = card
            return True
        return False

    def validate_addition(self, owner, trick="current"):
        if trick == "next":
            if self.next_trick_candidates[owner]:
                return False
        else:
            if self.current_trick[owner]:
                return False
        return True

    def find_card_owner(self, card):
        for player in self.players:
            if card in self.distribution[player]:
                return player

    def card_is_dummys(self, card):
        if card in self.distribution[self.dummy]:
            # print(card, self.distribution[self.dummy])
            return True
        return False  # google check for more pythonic way

    def ignore_dummy_cards():
        # ignore dummy cards when they show up on the table
        pass

    def increment_tricks_taken():
        pass

    def update_trickks():
        pass

    def update_cards_on_the_table():
        # w wersji testowej nie bedziemy tego uzywac, bo dostajemy od razu jak karty byly zagrywane przez cale rozdanie.
        pass

    def handle_trick_starting_player():
        pass

    def set_trick_orders(self):
        return [self.players_order[i:i + 4] for i in range(4)]

    def update_tricks_in_order():
        pass

    def start_deal(self):
        # start reading cards on the table every 2 seconds
        self.cards_snapshot_last = self.cards_seen_on_the_table[self.current_snapshot_index]
        while True:
            self.current_snapshot_index += 1
            print("\nnext loop iteration!")
            print("current trick length: {}".format(self.current_trick_length()))
            self.read_next_postiiton_on_the_table()
            print("current index: {}".format(self.current_snapshot_index))
            self.cards_snapshot_last = self.cards_seen_on_the_table[self.current_snapshot_index]
            self.cards_snapshot_last_but_one = self.cards_seen_on_the_table[self.current_snapshot_index - 1]
            if self.deal_over():
                print("here i am breaking the loop !!!")
                break
            time.sleep(1)

    def get_cards_every_second(self, cards_snapshot_last, cards_snapshot_last_but_one):
        self.cards_snapshot_last = cards_snapshot_last
        self.cards_snapshot_last_but_one = cards_snapshot_last_but_one
        self.current_snapshot_index += 1
        print(self.cards_snapshot_last)
        print(self.cards_snapshot_last_but_one)
        print("current trick length: {}".format(self.current_trick_length()))
        self.read_next_postiiton_on_the_table()
        print("current index: {}".format(self.current_snapshot_index))
        #Xself.return_sth_to_print()

    def deal_over(self):
        if len(self.cards_seen_on_the_table) == self.current_snapshot_index + 1:
            return True
        return False


def main():
    distribution_filename = "json/distribution.json"
    with open(distribution_filename) as file:
        distribution = json.load(file)
    contract = "2SE"
    cards_on_the_table_filename = "json/deal.json"
    only_cards = []
    with open(cards_on_the_table_filename) as file:
        for line in file:
            lines = [line] + list(itertools.islice(file, 2))
            cards_on_the_table = json.loads(''.join(lines))
            only_cards.append(cards_on_the_table["cards_played"])
    deal = dealHandler(distribution, contract, only_cards)
    deal.start_deal()
    print(deal.tricks)


# for i in deal.players:
#	print(deal.tricks[i])
# for i in range(13):
#	print(deal.tricks_in_order[i])


if __name__ == '__main__':
    main()
