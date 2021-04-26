# -*- coding: utf-8 -*-
"""
Social Influence Model
"""

import random
from enum import Enum, IntEnum
import matplotlib.pyplot as plt
from copy import deepcopy
import networkx as nx
from pylab import *
import pycxsimulator
import os
os.chdir('/Users/zoeychopra/Box/G1/CMPLXSYS 530 Marisa Eisenberg/')


timesteps = 100
simulations = 100
prevalence_array = np.zeros([timesteps, simulations])

N = 10
k = 2
p = 0.2
seed = 100


def initialize():
    global g, nextg, prevalence

    prevalence = []

    # use newman watts strogatz network with n nodes, k connected neighbors, p probability of rewiring edges, seed
    g = nx.newman_watts_strogatz_graph(N, k, p, seed)
    g.pos = nx.spring_layout(g)  # create initial position for nodes

    # each node gets attribute called state where 0 := susceptible
    nx.set_node_attributes(g, 0, 'state')
    for n in g.nodes:
        g._node[n]['state'] = random.randint(0, 1)
    g._node[1]['state'] = 1  # node 1 starts with state 1 := influencer signal

    # each node gets attribute called influencer
    nx.set_node_attributes(g, 0, 'influencer')
    g._node[1]['influencer'] = 1  # node 1 is the influencer

    labels = {}
    labels[1] = "Influencer"
    for i in range(2, len(g.nodes)):
        labels[i] = "Seeker"

    nextg = g.copy()
    nextg.pos = g.pos
    prevalence.append(1/len(g.nodes))


def update():
    global g, nextg, prevalence
    curprev = 0
    nextg = deepcopy(g)  # current and next time steps are totally separate

    for a in g.nodes:
        if g._node[a]['influencer'] == 1:  # if influencer
            nextg._node[a]['influencer'] = 1
            nextg._node[a]['state'] = 1

        if g._node[a]['influencer'] == 0:  # if seeker
            nextg._node[a]['influencer'] = 0

            value = 0
            total = 0
            for b in g.neighbors(a):
                if g._node[b]['state'] == 1:
                    value += 1
                    total += 1
                if g._node[b]['state'] == 0:
                    total += 1

            avg = value/total

            if avg < 0.5:
                nextg._node[a]['state'] = 0
            if avg == 0.5:
                nextg._node[a]['state'] = randint(0, 2)
            if avg > 0.5:
                nextg._node[a]['state'] = 1

        if g._node[a]['state'] == 1:
            curprev += 1

    g = deepcopy(nextg)
    prevalence.append(curprev/len(g.nodes))


def observe():
    global g, prevalence
    cla()
    nx.draw_networkx(g, cmap=cm.Wistia, vmin=0, vmax=1,
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

# Graph Prevalence
colors = np.random.randint(100, size=(len(prevalence)))
prevalence_graph = scatter(range(len(prevalence)),
                           prevalence, c=colors, cmap='viridis')
xlabel("Time")
ylabel("Prevalence of Influencer Signal")
show(prevalence_graph)
