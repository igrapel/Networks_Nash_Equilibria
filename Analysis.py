import matplotlib.pyplot as plt
import networkx as nx
import random
import numpy as np
import copy
import os
#import pandas as pd
os.chdir('C:\\Users\\ilang\OneDrive\\Desktop\\Projects\\Regret')
import CBG as Game
import Minimization as m


class PlotPoint:
  def __init__(self, strat_num, percent):
    self.strat_num = strat_num
    self.percent = percent

  def __lt__(self, other):
    return self.percent < other.percent

  def __str__(self):
    return f'Strat Num {self.strat_num} Probability {self.percent}'

def plot_strategy_box(strategy, title=None, color='blue'):
  x = np.arange(len(strategy))

  y = strategy
  
  plt.figure(figsize=(20, 8))
  plt.xticks(np.arange(0, len(x)))
  plt.bar(x, y, alpha=1, color=color)
  plt.axhline(strategy.mean(), color='red', linewidth=2)
  plt.ylabel('Probability')
  plt.xlabel('Strategy Number')
  plt.title(title)

  new_x = []
  new_y = []
  for i, perc in enumerate(strategy):
    if perc > strategy.mean():
      new_x.append(i)
      new_y.append(perc)
  plt.bar(new_x, new_y, alpha=.1, color='green')

def plot_strategy_box_2(random_strat, smart_strat, first='Random', second='Intelligent', sorted=False):
  if sorted:
    random_strat.sort()
    smart_strat.sort()

  x  = np.arange(len(random_strat))
  y  = random_strat
  x1 = np.arange(len(smart_strat))
  y1 = smart_strat
  
  plt.figure(figsize=(20, 8))
  plt.xticks(np.arange(0, len(x), 1))
  b1 = plt.bar(x,  y,  alpha=.5, color='blue')
  b2 = plt.bar(x1, y1, alpha=.5, color='green')
  plt.axhline(random_strat.mean(), color='red',  linewidth=2) # same for both
  plt.ylabel('Probability')
  plt.xlabel('Strategy Number')
  plt.title(f'{first} vs. {second}')
  plt.legend([b1, b2], [first, second])

def graph_strategy(strategy, sorted=False):
  plot_point_arr = []
  for i, strat in enumerate(strategy):
    plot_point_arr.append(PlotPoint(i, strat))
  if sorted:
    plot_point_arr.sort()
  
  x = [p.strat_num for p in plot_point_arr]
  y = [p.percent for p in plot_point_arr]

  plt.figure(figsize=(20, 8))
  plt.xticks(np.arange(0, len(x)), x)
  plt.bar(x, y, alpha=.5, color='blue')
  plt.ylabel('Probability')
  plt.xlabel('Strategy Number')

def get_unplayable_actions(strategy, action_set):
  strats = []
  for i in range(len(strategy)):
    if strategy[i] == 0:
      strats.append(action_set[i])
  return np.array(strats)

def get_playable_actions(strategy, action_set):
  strats = []
  for i in range(len(strategy)):
    if strategy[i] != 0:
      strats.append(action_set[i])
  return np.array(strats)

def get_above_average_actions(strategy, action_set):
  strats = []
  for i in range(len(strategy)):
    if strategy[i] >= strategy.mean():
      strats.append(action_set[i])
  return np.array(strats)

def print_top_n_actions(strategy, action_set, n, print_=True):
  plot_point_arr = []
  for i in range(len(strategy)):
    plot_point_arr.append(PlotPoint(i, strategy[i]))
  plot_point_arr.sort(reverse=True)
  temp = []
  
  for i in range(n):
    print(f'{i+1}) {action_set[plot_point_arr[i].strat_num]} % {plot_point_arr[i].percent}')


#Analyze 
with open('6n_6r_enhanced_star_h.npy', 'rb') as f:
    pmh = np.load(f)
    
with open('6n_6r_enhanced_star_h.npy', 'rb') as f:
    pm = np.load(f)
    
  
alg = m.Regret([(0, 1),(1, 2),(2, 3),(3, 4),(4, 5), (6,6)], 6, util_func='o', loaded_pm = pmh) 
top = alg.topology_edges
view = nx.Graph()
view.add_edges_from(top) 
nx.draw(view, with_labels=True)
alg.train(1000, intelligent_defender=True, intelligent_attacker=True)
print(print_top_n_actions(alg.attacker_strategy, alg.actions, 10))
