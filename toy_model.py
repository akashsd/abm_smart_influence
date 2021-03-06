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

timesteps = 20
simulations = 10
prevalence_array = np.zeros([timesteps, simulations])
influencer_array = np.zeros([timesteps, simulations])
seeker_array = np.zeros([timesteps, simulations])

N = 10  # number of nodes
k = 2  # number of connected neighbors for Watts-Strogatz network
p = 0.2  # probability of rewiring edges for Watts-Strogatz network
seed = 100  # seed value

likert = 5

base_pay = 16


def initialize():
    global g, nextg, prevalence, true, influencer_pay, seeker_pay

    prevalence = []
    influencer_pay = []
    seeker_pay = []

    #g = nx.complete_graph(N) # use complete graph
    # use newman-watts-strogatz network
    g = nx.newman_watts_strogatz_graph(N, k, p, seed)
    g.pos = nx.spring_layout(g)  # create initial position for nodes

    # each node gets attribute called state where 0 := susceptible
    nx.set_node_attributes(g, 0, 'state')
    for n in g.nodes:
        g._node[n]['state'] = random.randint(0, likert - 1)
    g._node[0]['state'] = random.randint(round((likert - 1)/2), likert - 1)

    # each node gets attribute called influencer
    nx.set_node_attributes(g, 0, 'influencer')
    g._node[0]['influencer'] = 1  # node 0 is the influencer

    # each node gets attribute called payoff
    nx.set_node_attributes(g, 0, 'payoff')
    true = 0
    for m in g.nodes:
        if g._node[m]['influencer'] == 1:
            # influencer node starts with base pay
            g._node[m]['payoff'] = base_pay
        if g._node[m]['influencer'] == 0:
            true = true + g._node[m]['state']
    true = true/(N-1)  # true average

    nextg = g.copy()
    nextg.pos = g.pos
    prevalence.append(1/len(g.nodes))
    influencer_pay.append(base_pay)
    seeker_pay.append(base_pay)


def update():
    global g, nextg, prevalence, true, influencer_pay, seeker_pay
    curprev = 0
    nextg = deepcopy(g)  # current and next time steps are totally separate

    for a in g.nodes:

        seeker_value = 0
        seeker_total = N-1
        seeker_avg = 0

        neighbor_value = 0
        neighbor_total = 0
        neighbor_avg = 0

        seeker_payoff = 0
        influencer_payoff = 0

        for b in g.neighbors(a):
            neighbor_value = neighbor_value + g._node[b]['state']
            neighbor_total += 1
        neighbor_avg = neighbor_value/neighbor_total

        if g._node[a]['influencer'] == 0:  # if seeker
            nextg._node[a]['influencer'] = 0

            seeker_payoff = g._node[a]['payoff']

            for i in range(0, likert):

                if abs(neighbor_avg - i) < 0.5:
                    nextg._node[a]['state'] = i
                if (neighbor_avg - i) == 0.5:
                    nextg._node[a]['state'] = random.randint(i, i+1)
                if (neighbor_avg - i) == -0.5:
                    nextg._node[a]['state'] = random.randint(i-1, i)

            seeker_value = seeker_value + nextg._node[a]['state']
            nextg._node[a]['payoff'] = base_pay - \
                (true - nextg._node[a]['state'])**2
            seeker_payoff = seeker_payoff + nextg._node[a]['payoff']

        seeker_payoff = seeker_payoff/seeker_total
        seeker_avg = seeker_value/seeker_total

        if g._node[a]['influencer'] == 1:  # if influencer
            influencer_state = g._node[a]['state']
            influencer_payoff = g._node[a]['payoff']

            nextg._node[a]['payoff'] = base_pay - \
                (seeker_avg - nextg._node[a]['state'])**2

            influencer_payoff = influencer_payoff + nextg._node[a]['payoff']

            nextg._node[a]['influencer'] = 1
            nextg._node[a]['state'] = g._node[a]['state']

        influencer_payoff = influencer_payoff/1

        if g._node[a]['state'] == influencer_state:
            curprev += 1

    g = deepcopy(nextg)
    prevalence.append(curprev/len(g.nodes))
    influencer_pay.append(influencer_payoff)
    seeker_pay.append(seeker_payoff)


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
    if i == 0:
        nx.draw_networkx(g, vmin=0, vmax=1, cmap='bwr',
                         node_color=[g._node[i]['influencer']
                                     for i in g.nodes],
                         pos=g.pos, with_labels=False)
        plt.show()
    for j in range(1, timesteps):  # loop over the timesteps for that simulation
        update()                  # update
    print("The current simulation being run is: %d " % (i + 1))
    print("The true value for this simulation is: {}".format(true))
    print()
    # store the resulting simulation in prevalence_array
    prevalence_array[:, i] = prevalence
    influencer_array[:, i] = influencer_pay
    seeker_array[:, i] = seeker_pay
prevalence_avg = prevalence_array.mean(axis=1)  # takes row average
influencer_avg = influencer_array.mean(axis=1)
seeker_avg = seeker_array.mean(axis=1)

# Graph Prevalence
for i in range(0, simulations):
    prevalence_graph = scatter(
        range(len(prevalence_array[:, i])), prevalence_array[:, i], alpha=0.05)
    plot(range(len(prevalence_array[:, i])),
         prevalence_array[:, i], alpha=0.05)
scatter(range(len(prevalence_avg)), prevalence_avg, color='black', alpha=1)
plot(range(len(prevalence_avg)), prevalence_avg, color='black', alpha=1)
title("Prevalence of Influencer Signal")
xlabel("Time")
ylabel("Prevalence")
plt.show()

# Graph Influencer Payoff
for i in range(0, simulations):
    influencer_graph = scatter(
        range(len(influencer_array[:, i])), influencer_array[:, i], alpha=0.05)
    plot(range(len(influencer_array[:, i])),
         influencer_array[:, i], alpha=0.05)
scatter(range(len(influencer_avg)), influencer_avg, color='black', alpha=1)
plot(range(len(influencer_avg)), influencer_avg, color='black', alpha=1)
title("Average Payoffs of Influencer")
xlabel("Time")
ylabel("Average Payoffs")
plt.show()

# Graph Seeker Payoff
for i in range(0, simulations):
    seeker_graph = scatter(
        range(len(seeker_array[:, i])), seeker_array[:, i], alpha=0.05)
    plot(range(len(seeker_array[:, i])), seeker_array[:, i], alpha=0.05)
scatter(range(len(seeker_avg)), seeker_avg, color='black', alpha=1)
plot(range(len(seeker_avg)), seeker_avg, color='black', alpha=1)
title("Average Payoffs of Seeker")
xlabel("Time")
ylabel("Average Payoffs")
plt.show()
