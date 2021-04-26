# -*- coding: utf-8 -*-
"""
Social Influence Model
"""

import os
os.chdir('C:/Users/Akash/Dropbox (University of Michigan)/2nd Sem/SI710_Tanya/Code/abm_smart_influence/')

import pycxsimulator
from pylab import * 
import networkx as nx 
from copy import deepcopy 
import matplotlib.pyplot as plt 
from enum import Enum, IntEnum 
import random 


timesteps = 200
simulations = 100
prevalence_array = np.zeros([timesteps, simulations])

N = 10
k = 2
p = 0.2
seed = 100

likert = 5


def initialize():
    global g, nextg, prevalence

    prevalence = []

    # use newman watts strogatz network with n nodes, k connected neighbors, p probability of rewiring edges, seed
    g = nx.newman_watts_strogatz_graph(N, k, p, seed)
    g.pos = nx.spring_layout(g)  # create initial position for nodes

    # each node gets attribute called state where 0 := susceptible
    nx.set_node_attributes(g, 0, 'state')
    for n in g.nodes:
        g._node[n]['state'] = random.randint(0, likert - 1)
    g._node[0]['state'] = random.randint(
        0, likert - 1)  # node 0 := influencer signal

    # each node gets attribute called influencer
    nx.set_node_attributes(g, 0, 'influencer')
    g._node[0]['influencer'] = 1  # node 0 is the influencer

    labels = {}
    labels[1] = "Influencer"
    for i in range(1, len(g.nodes)):
        labels[i] = "Seeker"

    nextg = g.copy()
    nextg.pos = g.pos
    prevalence.append(1/len(g.nodes))


def update():
    global g, nextg, prevalence
    curprev = 0
    nextg = deepcopy(g)  # current and next time steps are totally separate

    for a in g.nodes:
        value = 0
        total = 0

        for b in g.neighbors(a):
            value = value + g._node[b]['state']
            total += 1
        avg = value/total

        if g._node[a]['influencer'] == 1:  # if influencer
            nextg._node[a]['influencer'] = 1
            nextg._node[a]['state'] = g._node[a]['state']

        if g._node[a]['influencer'] == 0:  # if seeker
            nextg._node[a]['influencer'] = 0

            for i in range(0, likert):
                if abs(avg-i) < 0.5:
                    nextg._node[a]['state'] = i
                if (avg-i) == 0.5:
                    nextg._node[a]['state'] = random.randint(i, i+1)
                if (avg-i) == -0.5:
                    nextg._node[a]['state'] = random.randint(i-1, i)

        if g._node[a]['state'] == 1:
            curprev += 1

    g = deepcopy(nextg)
    prevalence.append(curprev/len(g.nodes))


def observe():
    global g, prevalence
    cla()
    nx.draw_networkx(g, cmap='Wistia', vmin=0, vmax=1,
                     #labels = labels, fontcolor = "whitesmoke", font_size = 20,
                     node_color=[g._node[i]['state'] for i in g.nodes],
                     pos=g.pos)


#pycxsimulator.GUI().start(func = [initialize, update, observe])

# Update Prevalence Array
for i in range(0, simulations):    # loop over all simulations
    initialize()                  # initialize each simulation
    for j in range(1, timesteps):  # loop over the timesteps for that simulation
        update()                  # update
    print("The current simulation being run is: %d " % (i + 1))
    # store the resulting simulation in prevalence_array
    prevalence_array[:, i] = prevalence

#Graph Prevalence
prevalence_avg = prevalence_array.mean(axis=1) #takes row average

plt.scatter(range(len(prevalence_avg)), prevalence_avg, alpha=0.1)
plt.xlabel("Time")
plt.ylabel("Prevalence of Influencer Signal")
plt.show()
plt.savefig('plot%d.png' % i)



# Graph Prevalence
# for i in range(0,simulations):
#     plt.scatter(range(len(prevalence_array[:, i])),
#                 prevalence_array[:, i])
#     plt.xlabel("Time")
#     plt.ylabel("Prevalence of Influencer Signal")
#     plt.text(2, .5, "Simulation Number: %d" %i)
#     # plt.show()
#     plt.savefig('plot%d.png' %i)



# colors = np.random.randint(100, size=(len(prevalence)))
# plt.scatter(range(len(prevalence)),
#             prevalence, c=colors, cmap='viridis')
# xlabel("Time")
# ylabel("Prevalence of Influencer Signal")
# plt.show()
