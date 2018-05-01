import json
import itertools
import time


class DealHandler(object):
    def __init__(self, distribution, contract):
        self.players_order = ["N", "E", "S", "W", "N", "E", "S", "W"]
        self.players = ["N", "E", "S", "W"]
        self.distribution = distribution
        self.cards_played = {"N": [], "S": [], "E": [], "W": []}
        self.cards_candidates = {"N": [], "S": [], "E": [], "W": []}
        self.cards_unplayed = dict(distribution)
        self.contract = contract
        self.tricks_taken = {"N": 0, "S": 0, "E": 0, "W": 0}
        self.cards_seen_on_the_table = []  # to co przychodzi co 2 sekundy spakowane do jednego slownika.
        self.current_snapshot_index = 0
        self.cards_snapshot_last = []
        self.cards_snapshot_last_but_one = []
        self.tricks = {"N": [''] * 13, "S": [''] * 13, "E": [''] * 13, "W": [''] * 13}
        self.declarer = self.resolve_declarer()
        self.dummy = self.resolve_dummy()
        self.trumps = self.resolve_trumps()
        self.tricks_starting_players = [self.resolve_first_lead_player()]  # ["N", "W", ...] # indeks to nr lewy-1
        self.tricks_winners = [''] * 13
        self.trick_orders = self.set_trick_orders()
        self.tricks_in_order = {}
        self.current_trick_index = 0
        self.current_trick = {"N": "", "E": "", "S": "", "W": ""}
        self.current_trick_color = ""
        self.current_trick_starting_player = self.tricks_starting_players[self.current_trick_index]
        self.next_trick_candidates = {"N": "", "E": "", "S": "", "W": ""}
        self.cards_order = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        self.error = 0
        self.error_message = ""

    def move_card_to_candidates(self, card):
        # self.
        pass

    def resolve_declarer(self):
        return self.contract[2]

    def resolve_dummy(self):
        return self.players_order[self.players_order.index(self.declarer) + 2]

    def resolve_trumps(self):
        return self.contract[1]

    def resolve_first_lead_player(self):
        return self.players_order[self.players_order.index(self.declarer) + 1]

    @staticmethod
    def cards_with_same_color(cards, color):
        return [card for card in cards if card[-1] == color]

    def highest_card(self, cards):
        return max(cards, key=lambda x: self.cards_order.index(x[:-1]))

    def move_card_to_played(self):
        pass

    def get_current_trick_winner(self):
        self.set_current_trick_color()
        trick_list = self.current_trick.values()
        trump_cards = [card for card in trick_list if card[-1] == self.trumps]
        if trump_cards:
            winner_card = self.highest_card(trump_cards)
            return self.find_card_owner(winner_card)
        else:
            trick_color_cards = self.cards_with_same_color(trick_list, self.current_trick_color)
            winner_card = self.highest_card(trick_color_cards)
            return self.find_card_owner(winner_card)

    def set_current_trick_color(self):
        # print("current trick: {}".format(self.current_trick))
        self.current_trick_color = self.current_trick[self.tricks_starting_players[self.current_trick_index]][-1]

    def read_next_position_on_the_table(self):
        # print("last snapshot: \n {}".format(self.cards_snapshot_last))
        # print("last but one snapshot: \n {}".format(self.cards_snapshot_last_but_one))
        cards_showed_up = [x for x in set(self.cards_snapshot_last) if x not in set(self.cards_snapshot_last_but_one)]
        cards_hided = [x for x in set(self.cards_snapshot_last_but_one) if x not in set(self.cards_snapshot_last)]
        # print("cards showed up: {}".format(cards_showed_up))
        if cards_hided:
            self.on_cards_hided(cards_hided)
        if cards_showed_up:
            self.on_cards_showed_up(cards_showed_up)

    def on_cards_hided(self, cards_hided):
        dummies_cards = []
        for card in cards_hided:
            if self.card_is_dummys(card):
                dummies_cards.append(card)
        if len(dummies_cards) > 2:
            self.raise_error("ERROR !!! at least 2 dummy's card were hided!"
                             "\nDummies cards hided: {}\n".format(dummies_cards))
            return
        for card in dummies_cards:
            if self.add_to_trick(card):
                self.close_trick()
            else:
                if not self.add_to_next_trick(card):
                    self.raise_error("Couldn't add card ({}) to the next trick".format(card))

    def on_cards_showed_up(self, cards_showed_up):
        dummies_cards = []
        other_cards = []
        for card in cards_showed_up:
            if self.card_is_dummys(card):
                dummies_cards.append(card)
            else:
                other_cards.append(card)
        # print("dummies cards {}".format(dummies_cards))
        # print("other cards {}".format(other_cards))
        # print("distribution: {}".format(self.distribution))
        for card in other_cards:
            if self.add_to_trick(card):
                self.close_trick()
            else:
                if not self.add_to_next_trick(card):
                    self.raise_error("Couldn't add card ({}) to the next trick".format(card))

    def raise_error(self, message):
        self.error = 1
        self.error_message = message

    def close_trick(self):
        if self.current_trick_length() == 4:
            self.tricks_winners[self.current_trick_index] = self.get_current_trick_winner()
            self.tricks_starting_players.append(self.tricks_winners[self.current_trick_index])
            self.move_current_trick_to_played()
            self.move_next_trick_to_current()
            self.current_trick_index += 1

    def move_current_trick_to_played(self):
        for key, value in self.current_trick.items():
            self.tricks[key][self.current_trick_index] = value
            self.cards_played[key] += self.cards_unplayed[key].pop(self.cards_unplayed[key].index(value))

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
        if self.validate_addition(owner, card):
            self.current_trick[owner] = card
            return True
        return False

    def add_to_next_trick(self, card):
        owner = self.find_card_owner(card)
        if self.validate_addition(owner, card, "next"):
            self.next_trick_candidates[owner] = card
            return True
        return False

    def validate_addition(self, owner, card, trick="current"):
        print("validating addition: owner {}, card {}, trick {}".format(owner, card, trick))
        if card in self.cards_played[owner]:
            self.raise_error("Card {} already played by player {}.".format(card, owner))
            return False
        if trick == "next":
            if self.next_trick_candidates[owner]:
                return False
        else:
            if self.current_trick[owner]:
                return False
        print("validation passed for card {} for owner {} for trick {}".format(
            card, owner, trick
        ))
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
            self.resolve_snapshots()
            self.read_next_position_on_the_table()
            print("current index: {}".format(self.current_snapshot_index))
            self.cards_snapshot_last = self.cards_seen_on_the_table[self.current_snapshot_index]
            self.cards_snapshot_last_but_one = self.cards_seen_on_the_table[self.current_snapshot_index - 1]
            if self.deal_over():
                print("here i am breaking the loop !!!")
                break
            time.sleep(1)

    def resolve_snapshots(self):
        # print("self resolving snapshot last {}".format(self.cards_snapshot_last))
        self.cards_snapshot_last = [i[0] for i in self.cards_snapshot_last]
        # print("self resolving snapshot last {}".format(self.cards_snapshot_last))
        # print("self resolving snapshot last but one {}".format(self.cards_snapshot_last_but_one))
        self.cards_snapshot_last_but_one = [i[0] for i in self.cards_snapshot_last_but_one]
        # print("self resolving snapshot last but one {}".format(self.cards_snapshot_last_but_one))

    def get_cards_every_second(self, cards_snapshot_last, cards_snapshot_last_but_one):
        self.cards_snapshot_last = cards_snapshot_last
        self.cards_snapshot_last_but_one = cards_snapshot_last_but_one
        self.resolve_snapshots()
        self.read_next_position_on_the_table()

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
    print("deal tricks".format(deal.tricks))


# for i in deal.players:
#	print(deal.tricks[i])
# for i in range(13):
#	print(deal.tricks_in_order[i])


if __name__ == '__main__':
    main()
