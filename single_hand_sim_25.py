# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 13:26:10 2024

@author: devli
"""

from simulator import run_manual_sim

def main():   
    
    run_manual_sim(num_players=5, 
                   player_1_hand=['5H','10H','3H','6H','7H'], 
                   trump=None, 
                   rounds=1000, 
                   return_summary=False,
                   log=False)

if __name__ == "__main__":
    main()