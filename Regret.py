import matplotlib.pyplot as plt
import networkx as nx
import random
import numpy as np
import copy
#import pandas as pd
import os
os.chdir('C:\\Users\\ilang\OneDrive\\Desktop\\Projects\\Regret')
import CBG as Game

class Regret:
    
    def __init__(self, edges_array, resources, loaded_pm=None, util_func='other', honeypots=0):
        self.resources = resources
        self.topology_edges = edges_array
        #temp_graph = nx.Graph()
        #self.topology = temp_graph.add_edges_from(self.topology_edges)
        #self.num_nodes = self.topology.number_of_nodes()
        self.edges_repeated = [inner for outer in self.topology_edges for inner in outer]
        self.num_nodes = len(set(self.edges_repeated))
        self.actions = list(self.sums(self.num_nodes, self.resources))
        self.honeypots = honeypots
        #self.defenders_actions = list(self.sums(self.num_nodes-honeypots, self.resources))
        #self.attackers_actions = list(self.sums(self.num_nodes, self.resources))
        self.actions = list(self.sums(self.num_nodes, self.resources))
        self.util_func = util_func
        if loaded_pm is None:
          self.payoff_matrix = self.create_payoff_matrix_full(self.actions)
          #self.payoff_matrix = self.create_payoff_matrix_full_hp()
        else:
          self.payoff_matrix = loaded_pm 
        self.DEFENDER_ACTION_LENGTH = len(self.actions)
        self.ATTACKER_ACTION_LENGTH = len(self.actions)
        #self.DEFENDER_ACTION_LENGTH = len(self.defenders_actions)
        #self.ATTACKER_ACTION_LENGTH = len(self.attackers_actions)
        self.defender_strategy     = np.full((self.DEFENDER_ACTION_LENGTH), 1/self.DEFENDER_ACTION_LENGTH)
        self.defender_regret_sum   = np.zeros((self.DEFENDER_ACTION_LENGTH))
        self.defender_strategy_sum = 0
        self.attacker_strategy     = np.full((self.ATTACKER_ACTION_LENGTH), 1/self.ATTACKER_ACTION_LENGTH)
        self.attacker_regret_sum   = np.zeros((self.ATTACKER_ACTION_LENGTH))
        self.attacker_strategy_sum = 0
        self.defender_util_sum     = 0
        self.list_of_defender_strategies = []
        self.list_of_attacker_strategies = []

    # All Solutions within a generator
    # (Total Sum + Length - 1) Choose (Length - 1)   
    def sums(self, nodes, resources):
        if nodes == 1:
            yield [resources,]
        else:
            for value in range(resources + 1):
                for permutation in self.sums(nodes - 1, resources - value):
                    yield [value,] + permutation

    def reset_strategies(self, reset_defender=True, reset_attacker=True):
      self.defender_util_sum       = 0
      if reset_defender:
        self.defender_strategy     = np.full((self.DEFENDER_ACTION_LENGTH), 1/self.DEFENDER_ACTION_LENGTH)
        self.defender_regret_sum   = np.zeros((self.DEFENDER_ACTION_LENGTH))
        self.defender_strategy_sum = 0
      if reset_attacker:
        self.attacker_strategy     = np.full((self.ATTACKER_ACTION_LENGTH), 1/self.ATTACKER_ACTION_LENGTH)
        self.attacker_regret_sum   = np.zeros((self.ATTACKER_ACTION_LENGTH))
        self.attacker_strategy_sum = 0

    def utility(self, game, evaluation_function):
      if evaluation_function == "giant_c":
        return game.giant_component_length
      elif evaluation_function == "average_node":
        return game.average_node_connectivity
      elif evaluation_function == "better_connectivity":
        return game.get_my_connectivity()
      else:
        return game.giant_component_length + game.average_node_connectivity

    def reset_strategies(self, reset_defender=True, reset_attacker=True):
      if reset_defender:
        self.defender_strategy     = np.full((self.DEFENDER_ACTION_LENGTH), 1/self.DEFENDER_ACTION_LENGTH)
        self.defender_regret_sum   = np.zeros((self.DEFENDER_ACTION_LENGTH))
        self.defender_strategy_sum = 0
        self.defender_util_sum     = 0
      if reset_attacker:
        self.attacker_strategy     = np.full((self.ATTACKER_ACTION_LENGTH), 1/self.ATTACKER_ACTION_LENGTH)
        self.attacker_regret_sum   = np.zeros((self.ATTACKER_ACTION_LENGTH))
        self.attacker_strategy_sum = 0

    #Get all strategies
    def create_payoff_matrix_full(self, data):
        payoff_matrix = [[0]*len(data) for i in range(len(data))]
        print("Length of payoff matrix: ", len(payoff_matrix))
        for defense_strategy_index in range(len(data)):
            print(("Row: ", defense_strategy_index), end = " ")
            for attacker_strategy_index in range(len(data)):
                current_graph = nx.Graph()
                current_graph.add_edges_from(self.topology_edges)
                Simulation_Game = Game.Game(current_graph, self.resources)
                Simulation_Game.fight(show=False, d_strategy = data[defense_strategy_index], a_strategy = data[attacker_strategy_index])
                payoff_matrix[defense_strategy_index][attacker_strategy_index] = self.utility(Simulation_Game, self.util_func)
                #plt.clf()
        #print(len(payoff_matrix)) 
        payoff_matrix_np = np.array(payoff_matrix)
        return payoff_matrix_np

    #Get all strategies
    def create_payoff_matrix_full_hp(self):
        payoff_matrix = [[0]*len(self.attackers_actions) for i in range(len(self.defenders_actions))]
        #print(f'Def len {len(self.defenders_actions)} attacker len {len(self.attackers_actions)}')
        #print(np.array(payoff_matrix).shape)
        #print("Length of payoff matrix: ", len(payoff_matrix))
        for defense_strategy_index in range(len(self.defenders_actions)):
            #print(("Row: ", defense_strategy_index), end = " ")
            for attacker_strategy_index in range(len(self.attackers_actions)):
                current_graph = nx.Graph()
                current_graph.add_edges_from(self.topology_edges)
                Simulation_Game = Game(current_graph, self.resources)
                Simulation_Game.fight(show=False, d_strategy = self.defenders_actions[defense_strategy_index], a_strategy = self.attackers_actions[attacker_strategy_index])
                payoff_matrix[defense_strategy_index][attacker_strategy_index] = self.utility(Simulation_Game, self.util_func)
                #plt.clf()
        #print(len(payoff_matrix)) 
        payoff_matrix_np = np.array(payoff_matrix)
        return payoff_matrix_np
    
    # choosing strategy's index given the probability as elements
    def __get_action(self, strategy):
      rand_num = random.random()
      action_index = 0
      cumulative_probability = 0
      while(action_index < len(strategy) - 1):
        cumulative_probability += strategy[action_index]
        if rand_num < cumulative_probability:
          return action_index
        action_index += 1
      return action_index
    
    # updates both agents strategies given 
    def update_strategy(self, defender_action_idx, attacker_action_idx, intelligent_defender=True, intelligent_attacker=True):
      util = self.payoff_matrix[defender_action_idx, attacker_action_idx]
      self.defender_util_sum += util
    
      if intelligent_defender:
        # Update Defender
        for i in range(self.DEFENDER_ACTION_LENGTH):
          possible_util = self.payoff_matrix[i][attacker_action_idx]
          
          if util < possible_util: # a better strategy was possible
            global defender_strategy_sum
            difference = possible_util - util
            self.defender_regret_sum[i] += difference
            self.defender_strategy_sum  += difference
    
        for i in range(self.DEFENDER_ACTION_LENGTH):
          if self.defender_strategy_sum != 0:
            self.defender_strategy[i] = self.defender_regret_sum[i]/self.defender_strategy_sum
    
      if intelligent_attacker:
        # Update Attacker
        for i in range(self.ATTACKER_ACTION_LENGTH):
          possible_util = self.payoff_matrix[defender_action_idx][i]
          
          if util > possible_util:
            global attacker_strategy_sum
            difference = util - possible_util
            self.attacker_regret_sum[i] += difference
            self.attacker_strategy_sum  += difference
    
        for i in range(self.ATTACKER_ACTION_LENGTH):
          if self.attacker_strategy_sum != 0:
            self.attacker_strategy[i] = self.attacker_regret_sum[i]/self.attacker_strategy_sum

      self.list_of_defender_strategies.append(self.defender_strategy)
      self.list_of_attacker_strategies.append(self.attacker_strategy)
    
    def get_defender_action(self):
      return self.__get_action(self.defender_strategy)
    
    def get_attacker_action(self):
      return self.__get_action(self.attacker_strategy)

    def get_defender_NE_strategy(self):
      return sum(self.list_of_defender_strategies)/len(self.list_of_defender_strategies)

    def get_attacker_NE_strategy(self):
      return sum(self.list_of_attacker_strategies)/len(self.list_of_defender_strategies)
    
  
    def train(self, iterations, intelligent_defender=True, intelligent_attacker=True):
  
      #100,000 iterations takes around 10 seconds for 1 intelligent agent
    
      for i in range(iterations):
        self.update_strategy(self.get_defender_action(), self.get_attacker_action(), intelligent_defender, intelligent_attacker)
      return self.defender_util_sum / iterations

    def single_train(self, intelligent_defender=True, intelligent_attacker=True):
      a_action = self.get_attacker_action()
      d_action = self.get_defender_action()

      self.update_strategy(d_action, a_action, intelligent_defender, intelligent_attacker)
      return self.defender_util_sum, a_action, d_action
