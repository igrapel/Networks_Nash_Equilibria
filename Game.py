
import matplotlib.pyplot as plt
import networkx as nx
import random
import numpy as np
import requests
import re
import copy

from bisect import bisect_left

class Game:
    
    def __init__(self, topology, resources):
      """
      :param topology: Networkx Topology
      :param resources: The player's total amount of resources.
      """
      self.resources = resources
      self.topology = topology
      self.average_node_connectivity = nx.average_node_connectivity(self.topology)
      self.num_edges = self.topology.number_of_edges()
      self.num_nodes = self.topology.number_of_nodes()
      self.giant_component = self.getGiantComponent()
      self.giant_component_length = len(self.giant_component)
      #Array holds resource allocation. 
      #Ex.   [1,2,2,0]  for 5 resources and 4 nodes
      # Superfluous - the code passes this into a dictionary. 
      self.defender_resource_array = []
      self.attacker_resource_array = []
      self.defender = dict.fromkeys(range(0, self.num_nodes))
      self.attacker = dict.fromkeys(range(0, self.num_nodes))

 
    def fight(self, a_strategy = None, d_strategy = None, show = False):
      if(self.num_nodes < 1):
        print("No Graph.")
        return
    
      #Check for defender strategy. Otherwise, will play random strategy
      if(d_strategy==None):
        #create random arrays of resource allocation
        self.defender_resources_array = self.__get_rand_strategy(defender=True)
      else:
        self.defender_resources_array = d_strategy
    
      #Check for attacker strategy. Otherwise, will play random strategy
      if(a_strategy==None):
        #create random arrays of resource allocation
        self.attacker_resources_array = self.__get_rand_strategy()
      else:
        self.attacker_resources_array = a_strategy
    
      #assign the values to dicitonary nodes
      index = 0
      for node_d, node_a in zip(self.defender, self.attacker):
        self.defender[node_d] = self.defender_resources_array[index]
        self.attacker[node_a] = self.attacker_resources_array[index]
        index += 1

      #remove defeated nodes and update fields
      for n in list(self.topology.nodes()):
          if self.defender[n] < self.attacker[n]:
            # print(f'Lost drone {i}!')
            self.remove_network_node(n)
            #Deletes from the node-resource dictionary
            del self.defender[n]
            del self.attacker[n]
            #Update graph statistics
            self.num_edges = self.topology.number_of_edges()
            self.average_node_connectivity = nx.average_node_connectivity(self.topology)
            self.num_nodes = self.topology.number_of_nodes()
            self.giant_component = self.getGiantComponent()
            self.giant_component_length = len(self.giant_component)

      #show pre-attack resources 
      if(show):
          print("Post-fight Arrangement: ")
          Gcc = sorted(nx.connected_components(self.topology ), key=len, reverse=True)
          giant_component = self.topology.subgraph(Gcc[0])
          print(f'''Average Node Connectivity: {self.average_node_connectivity}\nGiant Component {self.giant_component} 
    Giant Component Length: {self.giant_component_length} \nEdges: {self.num_edges}\nNodes: {self.num_nodes} \nAttacker\'s Node Allocation: {self.attacker}
    Defender\'s Node Allocation: {self.defender}\n''')
    
    def __get_rand_strategy(self, defender=False):  
      random_resources = random.sample(range(1, self.resources), self.num_nodes -1) + [0, self.resources]
      list.sort(random_resources)
      resources_array = [random_resources[i+1] - random_resources[i] for i in range(len(random_resources) - 1)]

      return resources_array

    def remove_network_node(self, node):
      self.topology.remove_node(node)
      # save topology with new graph
      
    #Gets giant connected component
    def getGiantComponent(self):
      if(len(self.topology) == 0):
          return {}
      Gcc = sorted(nx.connected_components(self.topology), key=len, reverse=True)
      return Gcc[0]

    def get_my_connectivity(self):
      return self.topology.number_of_edges()

    def draw_game(self, color='cyan'):
      nx.draw(self.topology, node_color = color, node_size = 300, with_labels=True)

    def __str__(self):
      return f'''Average Node Connectivity: {self.average_node_connectivity}\nGiant Component {self.giant_component}Giant Component Length: {self.giant_component_length} \nEdges: {self.num_edges}\nNodes: {self.num_nodes} \nAttacker\'s Node Allocation: {self.attacker}
    Defender\'s Node Allocation: {self.defender}\n'''

'''
current_graph = nx.Graph()
current_graph.add_edges_from([(0,1), (1,2), (2,3)])
t = Game(current_graph, 4)

t.fight()
t.draw_game()
print(t.get_my_connectivity())
'''
