class NE_regret:
    
    def __init__(self, edges_array, resources):
        self.resources = resources
        self.topology_edges = edges_array
        #temp_graph = nx.Graph()
        #self.topology = temp_graph.add_edges_from(self.topology_edges)
        #self.num_nodes = self.topology.number_of_nodes()
        self.strategies_gen = list(self.sums(5, self.resources))
        self.payoff_matrix = self.create_payoff_matrix_full(self.strategies_gen)
        self.DEFENDER_ACTION_LENGTH = len(self.strategies_gen)
        self.ATTACKER_ACTION_LENGTH = len(self.strategies_gen)
        self.defender_strategy     = np.full((self.DEFENDER_ACTION_LENGTH), 1/self.DEFENDER_ACTION_LENGTH)
        self.defender_regret_sum   = np.zeros((self.DEFENDER_ACTION_LENGTH))
        self.defender_strategy_sum = 0
        self.attacker_strategy     = np.full((self.ATTACKER_ACTION_LENGTH), 1/self.ATTACKER_ACTION_LENGTH)
        self.attacker_regret_sum   = np.zeros((self.ATTACKER_ACTION_LENGTH))
        self.attacker_strategy_sum = 0
        
    def sums(self, length, total_sum):
        if length == 1:
            yield [total_sum,]
        else:
            for value in range(total_sum + 1):
                for permutation in self.sums(length - 1, total_sum - value):
                    yield [value,] + permutation
    
    #Get all strategies
    def create_payoff_matrix_full(self, data):
        payoff_matrix = [[0]*len(data) for i in range(len(data))]
        for defense_strategy_index in range(len(data)):
            for attacker_strategy_index in range(len(data)):
                current_graph = nx.Graph()
                current_graph.add_edges_from(self.topology_edges)
                Simulation_Game = Game(current_graph, self.resources)
                Simulation_Game.fight(show=False, d_strategy = data[defense_strategy_index], a_strategy = data[attacker_strategy_index])
                payoff_matrix[defense_strategy_index][attacker_strategy_index] = Simulation_Game.giant_component_length
                plt.clf()
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
    
      if intelligent_defender:
        # Update Defender
        for i in range(self.DEFENDER_ACTION_LENGTH):
          possible_util = self.payoff_matrix[i][attacker_action_idx]
          
          if util < possible_util: # a better strategy was possible
            global defender_strategy_sum
            difference = util - possible_util
            self.defender_regret_sum[i] += difference
            self.defender_strategy_sum  += difference
    
        for i in range(self.DEFENDER_ACTION_LENGTH):
          if self.defender_strategy_sum != 0:
            self.defender_strategy[i] = self.defender_regret_sum[i]/self.defender_strategy_sum
    
      if intelligent_attacker:
        # Update Attacker
        for i in range(self.ATTACKER_ACTION_LENGTH):
          possible_util = self.payoff_matrix[defender_action_idx][i]
          
          if util < possible_util:
            global attacker_strategy_sum
            difference = util - possible_util
            self.attacker_regret_sum[i] += difference
            self.attacker_strategy_sum  += difference
    
        for i in range(self.ATTACKER_ACTION_LENGTH):
          if self.attacker_strategy_sum != 0:
            self.attacker_strategy[i] = self.attacker_regret_sum[i]/self.attacker_strategy_sum
    
    def get_defender_action(self):
      return self.__get_action(self.defender_strategy)
    
    
    def get_attacker_action(self):
      return self.__get_action(self.attacker_strategy)
    # training function
    
    def train(self, iterations, intelligent_defender=True, intelligent_attacker=True):
      '''
      100,000 iterations takes around 10 seconds for 1 intelligent agent
      '''
      for i in range(iterations):
        self.update_strategy(self.get_defender_action(), self.get_attacker_action(), intelligent_defender, intelligent_attacker)
    
test_graph = nx.Graph()
test_graph.add_edges_from([(0,1), (1,2), (2,3), (3,4)])


nx.draw(test_graph, node_size = 300, with_labels=True)

t = NE_regret([(0,1), (1,2), (2,3), (3,4)], 6)
t.train(2000, intelligent_defender = True, intelligent_attacker = False)
ds = t.defender_strategy
strats = t.strategies_gen
