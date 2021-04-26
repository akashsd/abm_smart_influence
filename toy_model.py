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

p_i = 0.5  # Pr(infection per contact)
p_r = 0.5  # Pr(recovery)
p_b = 0.5  # Pr(breaking tie with infected contact)
p_a = 0.5  # Pr(adding a tie back after infection has resolved)

prevalence = []
signal_number = 5


def initialize():
    global g, nextg, prevalence
    # use newman watts strogatz network with n nodes, k connected neighbors, p probability of rewiring edges, seed
    g = nx.newman_watts_strogatz_graph(10, 2, .2, 100)
    g.pos = nx.spring_layout(g)  # create initial position for nodes

    # each node gets attribute called state where 0 := susceptible
    nx.set_node_attributes(g, 0, 'state')
    for n in g.nodes:
        g._node[n]['state'] = random.randint(0, signal_number-1)
    # node 1 starts with state 1 := influencer signal
    g._node[1]['state'] = random.randint(0, signal_number-1)

    # each node gets attribute called influencer
    nx.set_node_attributes(g, 0, 'influencer')
    g._node[1]['influencer'] = 1  # node 1 is the influencer

    labels = {}
    labels[1] = "Influencer"
    for i in range(2, len(g.nodes)):
        labels[i] = "Seeker"

    nextg = g.copy()
    nextg.pos = g.pos
    prevalence.append(1/len(g.nodes))  # What does append do here?


def update():
    global g, nextg, prevalence
    curprev = 0  # ???
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

            for i in range(0, signal_number):
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
    nx.draw_networkx(g,  vmin=0, vmax=4,
                     #labels = labels, fontcolor = "whitesmoke", font_size = 20,
                     node_color=[g._node[i]['state'] for i in g.nodes],
                     pos=g.pos)


pycxsimulator.GUI().start(func=[initialize, update, observe])

prevalence_graph = scatter(range(len(prevalence)), prevalence)
xlabel("Time")
ylabel("Prevalence")
show(prevalence_graph)
