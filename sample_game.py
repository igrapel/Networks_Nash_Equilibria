plt.clf()

#Enhanced STar
enhanced_star_type = nx.star_graph(3)
enhanced_star_type.add_edges_from([(1,2)])
nx.draw(enhanced_star_type, node_color = 'pink', node_size = 300, with_labels=True)


Simulation_Game = Game(enhanced_star_type, 5)
Simulation_Game.fight(d_strategy = [0,3,2,0], a_strategy = [0,3,0,2])

Simulation_Game.draw_game('cyan')
