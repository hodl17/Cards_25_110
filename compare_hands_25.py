# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 13:31:37 2024

@author: devli
"""

from simulator import sim_hand_combinations

def main():
    hands = [
            ['5H', 'JH', 'AH', 'KH', 'QH'],
            ['5D', 'JD', 'AD', 'KD', 'QD'],
            ['2H', '3H', '4H', '6H', '7H'],
            ]
    
    sim_hand_combinations(hands_test=hands, 
                          num_players=5, 
                          trump=None, 
                          rounds=10000,
                          log=False)

if __name__ == "__main__":
    main()