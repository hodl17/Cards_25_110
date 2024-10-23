# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 11:43:28 2024

@author: devli
"""

import random
import sys
import itertools
import tabulate
import matplotlib.pyplot as plt

class Card:
    
    def __init__(self, suit, value):
        self.suit = suit
        self.value = str(value)
        self.name = self.name()
        
    def name(self):
        return self.value + self.suit
    
    
class Rank:
    def __init__(self, card, trump):
        self.card = card
        self.trump = trump
        self.rank = self.rank()
        
    def rank(self):
        if self.card.suit in ['H', 'D']:
            ranks = {
                    'A': 13, 'K': 12, 'Q': 11, 'J': 10, '10': 9, '9': 8, '8': 7,
                    '7': 6, '6': 5, '5': 4, '4': 3, '3': 2, '2': 1
                    }
        else:
            # low is high for black suits
            ranks = {
                    'A': 13, 'K': 12, 'Q': 11, 'J': 10, '2': 9, '3': 8, '4': 7,
                    '5': 6, '6': 5, '7': 4, '8': 3, '9': 2, '10': 1
                    }
            
        suit_ranks = {
                'H': 40, 'C': 27, 'D': 14, 'S': 1
                }
        
        if self.trump==self.card.suit:
            # make trumps more valuable and AH the 3rd best
            ranks.update((x, y+53) for x, y in ranks.items())
            ranks['5'] = max(ranks.values())+3
            ranks['J'] = ranks['5']-1
            
        rank = ranks[self.card.value] + suit_ranks[self.card.suit]
        
        if self.card.name=='AH' and self.trump in ['C', 'S', 'D']:
            # make sure AH is third highest for any trump
            # sad to hardcode these numbers
            rank = suit_ranks[self.trump] + 13 + 53 + 3 - 2
        
        return rank
        
class Deck:
    def __init__(self):
        self.suits = ['H', 'C', 'D', 'S']
        self.cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A']
        self.deck = self.make_deck()
        
    def make_deck(self):
        deck = []
        for suit in self.suits:
            for card in self.cards:
                deck.append(Card(suit, card))
                
        return deck
    
    def shuffle_deck(self):
        return random.shuffle(self.deck)
    
    def deal_hand(self, no_cards, no_hands):
        assert no_cards*no_hands<=len(self.deck), "Trying to deal {} cards but there are only {} in the deck!".format(no_cards*no_hands, len(self.deck))
        
        hands = []
        for i in range(no_hands):
            hand = []
            for j in range(no_cards):
                hand.append(self.deck[0])
                self.deck.remove(self.deck[0])
            hands.append(hand)
            
        return hands
    
    def deal(self, hands=1, cards_per_hand=5, shuffle=True):
        if shuffle:
            self.shuffle_deck()
        
        return self.deal_hand(cards_per_hand, hands)
    
    def deal_specific_hand(self, cards):
        """
        Allow a specific hand to be dealt if you pass in a string of card names.
        """
        hand = []
        for card in self.deck:
            if card.name in cards:
                hand.append(card)
        self.deck = [x for x in self.deck if x not in hand]
            
        return hand
    
    def all_hand_combinations(self):
        all_cards = self.make_deck()
        all_hands = itertools.combinations(all_cards, 5)
        return list(all_hands)


class BasicStrategy:
    def __init__(self, player, cards_played, leading_card):
        self.player = player
        self.cards_played = cards_played
        self.leading_card = leading_card
        
    def play_card(self):
        if self.cards_played:
            if self.leading_card.suit == TRUMP and self.player.has_trumps():
                if Rank(self.player.top_trump(), TRUMP).rank > max([Rank(c, TRUMP).rank for c in self.cards_played.values()]):
                    card = self.player.top_trump()
                    
                else:
                    card=self.player.worst_trump()
            
            elif Rank(self.player.best_card(), TRUMP).rank > max([Rank(c, TRUMP).rank for c in self.cards_played.values()]):
                card=self.player.best_card()
                
            else:
                card=self.player.worst_card()
        else:
            card=self.player.best_card()
            
        return card


class TopperStrategy(BasicStrategy):
    def __init__(self, player, cards_played, leading_card):
        self.player = player
        self.cards_played = cards_played
        self.leading_card = leading_card
        super(TopperStrategy, self).__init__(player, cards_played, leading_card)
        
    def play_card(self):
        if self.cards_played:
            if self.leading_card.suit == TRUMP and self.player.has_trumps():
                card=self.player.worst_trump()
                winning_trump_ranks = {}
                for trump in self.player.trumps():
                    if Rank(trump, TRUMP).rank > max([Rank(c, TRUMP).rank for c in self.cards_played.values()]):
                        winning_trump_ranks[trump] = Rank(trump, TRUMP).rank
                if winning_trump_ranks:
                    card = min(winning_trump_ranks, key=winning_trump_ranks.get)
            
            elif Rank(self.player.best_card(), TRUMP).rank > max([Rank(c, TRUMP).rank for c in self.cards_played.values()]):
                winning_card_ranks = {}
                for card in self.player.hand:
                    if Rank(card, TRUMP).rank > max([Rank(c, TRUMP).rank for c in self.cards_played.values()]):
                        winning_card_ranks[card] = Rank(card, TRUMP).rank
                card = min(winning_card_ranks, key=winning_card_ranks.get)
                
            else:
                card=self.player.worst_card()
        else:
            card=self.player.worst_card()
            
        return card

   
class Player:
    def __init__(self, name):
        self.name = 'player{}'.format(name)
        self.hand = []
        self.points = 0
        self.best_card_points = 9
        self.tricks_won = 0
        self.strategy = BasicStrategy
        
    def total_hand_rank(self):
        return sum([Rank(c, TRUMP).rank for c in self.hand])
    
    def hand_ranks(self):
        return {c:Rank(c, TRUMP).rank for c in self.hand}
    
    def print_hand(self):
        return [c.name for c in self.hand]
        
    def trumps(self):
        return [c for c in self.hand if c.suit==TRUMP]
    
    def has_trumps(self):
        if self.trumps():
            return True
        return False
    
    def top_trump(self):
        trump_ranks = {c:Rank(c, TRUMP).rank for c in self.trumps()}
        return max(trump_ranks, key=trump_ranks.get)
    
    def worst_trump(self):
        trump_ranks = {c:Rank(c, TRUMP).rank for c in self.trumps()}
        return min(trump_ranks, key=trump_ranks.get)
    
    def best_card(self):
        return max(self.hand_ranks(), key=self.hand_ranks().get)
    
    def worst_card(self):
        return min(self.hand_ranks(), key=self.hand_ranks().get)
    
    def plays_card(self, card):
        self.hand.remove(card)
    
    def draws_cards(self, number=2):
        new_cards = DECK.deal(hands=1, cards_per_hand=number, shuffle=False)[0]
            
        self.hand+=new_cards
        
    def pick_card_to_play(self, cards_played, leading_card):
        card = self.strategy(self, cards_played, leading_card).play_card()
        self.plays_card(card)
        return card
        

def get_trump():
    card = DECK.deal(hands=1, cards_per_hand=1, shuffle=False)[0][0]
    global TRUMP
    TRUMP = card.suit

def rank_trick(cards, log=False):
    
    winner = None
    winning_card = None
    winning_card_rank = 0
    for player, card in cards.items():
        rank = Rank(card, TRUMP).rank
        if rank > winning_card_rank:
            winner = player
            winning_card = card
            winning_card_rank = rank
    if log:
        print('{} wins with {}'.format(winner.name, winning_card.name))
    winner.points+=5
    winner.tricks_won+=1
    
    # print('{} wins with {}'.format(winner.name, winning_card.name))
    
    return winner, winning_card
    

def play_round(players, start_index, log=False):
    """
    Play a round of 5 tricks
    """
       
    best_this_round = ('', '', 0)
    
    for i in range(5):
        cards_played = {}
        leading_card = Card('S', 10)
        player_list = list(players.values())
        player_list = player_list[start_index:] + player_list[:start_index]
        
        for player in player_list: 
            card = player.pick_card_to_play(cards_played, leading_card)
            
            if log:
                print('{} plays {}'.format(player.name, card.name))
            
            if not cards_played:
                leading_card = card
            cards_played[player]=card
                
        winner, winning_card = rank_trick(cards_played)
        if Rank(winning_card, TRUMP).rank > best_this_round[2]:
            best_this_round = (winner, winning_card, Rank(winning_card, TRUMP).rank)
            
        start_index = list(players.values()).index(winner)
            
    # add 5 points for whoever plays the best card
    best_this_round[0].points+=5
    best_this_round[0].best_card_points+=5
       
   
def plot_points(players):
    total_tricks = sum([x.tricks_won for x in players.values()])
    rounds = total_tricks/5
    
    plt.title('Average points per player')    
    plt.bar([p.name for p in players.values()], [p.points/rounds for p in players.values()])
    plt.show()
    
    
def summary_statistics(players):
    total_tricks = sum([x.tricks_won for x in players.values()])
    rounds = total_tricks/5
    table = []
    for player in players.values():
        row = []
        row.append(player.name)
        row.append(round(player.points/rounds,2))
        row.append(round(100*player.tricks_won/total_tricks))
        table.append(row)
    
    print(tabulate.tabulate(table, headers=['Player', 'Avg Points', 'Trick Win Pct']))
    
    
def summary_statistics_player1_only(players, player_1_hand):
    total_tricks = sum([x.tricks_won for x in players.values()])
    rounds = total_tricks/5
    return [player_1_hand, 
            round(players['player1'].points/rounds), 
            round(100*players['player1'].tricks_won/total_tricks,2)]
    
def run_25_sim(num_players = 5, rounds = 10000):
    players = {'player{}'.format(i+1):Player(i+1) for i in range(num_players)}
    
    for i in range(rounds):
    # create deck
        global DECK 
        DECK = Deck()
        
        # deal out hands
        hands = DECK.deal(hands=num_players)
        
        # assign hands to players
        for j in range(len(hands)):
            players['player{}'.format(j+1)].hand = hands[j]
        
        # get trump suit
        get_trump()
        # print('Trump: {}'.format(TRUMP))
        
        # play a round of 5 tricks
        play_round(players, start_index=i%num_players)
      
    summary_statistics(players)
    plot_points(players)
    
    
def run_manual_sim(num_players=5, player_1_hand=None, trump=None, rounds=1000, return_summary=False, log=False):
    players = {'player{}'.format(i+1):Player(i+1) for i in range(num_players)}
       
    for i in range(rounds):
    # create deck
        global DECK 
        DECK = Deck()
        
        players['player1'].hand = DECK.deal_specific_hand(player_1_hand)
        
        # deal out hands
        hands = DECK.deal(hands=num_players-1)
        
        # assign hands to players
        for j in range(0, num_players-1):
            players['player{}'.format(j+2)].hand = hands[j]
        
        if log:
            for player in players.values():
                print('{}: {}'.format(player.name, player.print_hand()))
        
        # get trump suit
        if not trump:
            get_trump()
        else:
            global TRUMP
            TRUMP = trump
        # print('Trump: {}'.format(TRUMP))
        
        # play a round of 5 tricks
        play_round(players, start_index=i%num_players, log=log)   
        
    if return_summary:
        return summary_statistics_player1_only(players, player_1_hand)
    else:
        if player_1_hand:
            print('player1 is playing with {} while rest are randomized'.format(player_1_hand))
        summary_statistics(players)
        plot_points(players)
    

def sim_hand_combinations(hands_test=None, num_players=5, trump=None, rounds=1000, log=False):
    """
    Run a sim on all hand combinations
    """
    if not hands_test:
        all_hands = Deck().all_hand_combinations()
    else:
        hands_test = [[Card(c[-1],c[:-1]) for c in h] for h in hands_test]
        all_hands = hands_test
    
    table = []
    for hand in all_hands:
        hand_str = [x.name for x in hand]
        table.append(run_manual_sim(num_players=num_players, player_1_hand=hand_str, 
                                    trump=trump, rounds=rounds, return_summary=True,
                                    log=log))
    
    print('Results for each hand when trump is {}'.format(trump))
    print(tabulate.tabulate(table, headers=['Hand', 'Avg Points', 'Trick Win Pct']))


def parse_card_input(player):
    print('Your turn..... your hand is {}'.format(player.print_hand()))
    input_card = str(input()) 
    if input_card=='exit':
        sys.exit()
    value, suit = input_card[:-1], input_card[-1]
    input_card_obj = Card(suit, value)
    card=None
    for c in player.hand:
        if c.name == input_card_obj.name:
            card = c
    return card, input_card


def play_round_as_player1(players, start_index, log=False):
    """
    Play a round of 5 tricks
    """
       
    best_this_round = ('', '', 0)
    
    for i in range(5):
        print('---------------------')
        cards_played = {}
        leading_card = Card('S', 10)
        player_list = list(players.values())
        player_list = player_list[start_index:] + player_list[:start_index]
        
        for player in player_list: 
            
            if player.name == 'player1':
                card, input_card = parse_card_input(player)
                        
                while not card:
                    print('{} is not possible. Please try again. Your current hand is {}'.format(input_card, player.print_hand()))
                    card, input_card = parse_card_input(player)
                    
                player.plays_card(card)
                
            else:
                card = player.pick_card_to_play(cards_played, leading_card)
            
            print('{} plays {}'.format(player.name, card.name))
            
            if not cards_played:
                leading_card = card
            cards_played[player]=card
                
        winner, winning_card = rank_trick(cards_played)
        if Rank(winning_card, TRUMP).rank > best_this_round[2]:
            best_this_round = (winner, winning_card, Rank(winning_card, TRUMP).rank)
            
        start_index = list(players.values()).index(winner)
            
    # add 5 points for whoever plays the best card
    best_this_round[0].points+=5
    best_this_round[0].best_card_points+=5

    
def play_25_as_player1(num_players=4, rounds=1, log=True):
    players = {'player{}'.format(i+1):Player(i+1) for i in range(num_players)}
    
    for i in range(rounds):
    # create deck
        global DECK 
        DECK = Deck()
        
        # deal out hands
        hands = DECK.deal(hands=num_players)
        
        # assign hands to players
        for j in range(len(hands)):
            players['player{}'.format(j+1)].hand = hands[j]
            
        print('Your Hand: {}'.format(players['player1'].print_hand()))
        
        # get trump suit
        get_trump()
        print('Trump suit: {}'.format(TRUMP))
        
        play_round_as_player1(players, i%num_players, log)
        
    summary_statistics(players)
    plot_points(players)
    
    
def run_25_strategy_sim(num_players=5, rounds=10000, strategy_map=None):
    players = {'player{}'.format(i+1):Player(i+1) for i in range(num_players)}
    
    if strategy_map:
        for player in players.values():
            try:
                player.strategy = strategy_map[player.name]
            except KeyError:
                # use BasicStrategy unless otherwise specified
                continue
    
    for i in range(rounds):
    # create deck
        global DECK 
        DECK = Deck()
        
        # deal out hands
        hands = DECK.deal(hands=num_players)
        
        # assign hands to players
        for j in range(len(hands)):
            players['player{}'.format(j+1)].hand = hands[j]
        
        # get trump suit
        get_trump()
        # print('Trump: {}'.format(TRUMP))
        
        # play a round of 5 tricks
        play_round(players, start_index=i%num_players)
      
    summary_statistics(players)
    plot_points(players)
