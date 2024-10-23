# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 15:26:36 2024

@author: devli
"""

from simulator import run_25_strategy_sim, TopperStrategy
    
def main():
    strategy_map = {'player1': TopperStrategy}
    
    run_25_strategy_sim(num_players=5, 
                        rounds=10000,
                        strategy_map = strategy_map)

if __name__ == "__main__":
    main()