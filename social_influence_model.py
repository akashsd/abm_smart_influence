# -*- coding: utf-8 -*-
"""
Social Influence Model
"""

import os
os.chdir('/Users/zoeychopra/Box/G1/CMPLXSYS 530 Marisa Eisenberg/')

#import pycxsimulator
from pylab import *
import networkx as nx
from copy import deepcopy
import matplotlib.pyplot as plt
from enum import Enum, IntEnum
import random

timesteps = 20
simulations = 5
prevalence_array = np.zeros([timesteps, simulations])  

N = 10
k = 2
p = 0.2
seed = 100

likert = 5

base_pay = 16


def initialize():
    global g, nextg, prevalence, true
    
    prevalence = []
    
    g = nx.newman_watts_strogatz_graph(N,k,p,seed) # use newman watts strogatz network with n nodes, k connected neighbors, p probability of rewiring edges, seed
    g.pos = nx.spring_layout(g) # create initial position for nodes
    
    nx.set_node_attributes(g, 0, 'state') # each node gets attribute called state where 0 := susceptible
    for n in g.nodes:
        g._node[n]['state'] = random.randint(0, likert - 1)

    nx.set_node_attributes(g, 0, 'influencer') # each node gets attribute called influencer
    g._node[0]['influencer'] = 1 # node 0 is the influencer
    
    nx.set_node_attributes(g, 0, 'payoff') # each node gets attribute called payoff
    true = 0
    for m in g.nodes:
        if g._node[m]['influencer'] == 1:
            g._node[m]['payoff'] = base_pay #influencer node starts with base pay
        if g._node[m]['influencer'] == 0:
            true = true + g._node[m]['state']
    true = true/(N-1) #true average
        
    
    # labels = {}
    # labels = labels.append("Influencer")
    # for i in range(1, len(g.nodes)):
    #     labels = labels.append("Seeker")
    
    nextg = g.copy()
    nextg.pos = g.pos
    prevalence.append(1/len(g.nodes))

def update():
    global g, nextg, prevalence, true
    curprev = 0
    nextg = deepcopy(g) # current and next time steps are totally separate
    
    for a in g.nodes:
        
        seeker_value = 0
        seeker_total = N-1
        seeker_avg = 0
        
        neighbor_value = 0
        neighbor_total = 0
        neighbor_avg = 0
        
        for b in g.neighbors(a):
            neighbor_value = neighbor_value + g._node[b]['state']
            neighbor_total += 1
        neighbor_avg = neighbor_value/neighbor_total
        
        
        if g._node[a]['influencer'] == 0: # if seeker
            nextg._node[a]['influencer'] = 0
            
            for i in range(0, likert):
                
                if abs(neighbor_avg - i) < 0.5:
                    nextg._node[a]['state'] = i
                if (neighbor_avg - i) == 0.5:
                    nextg._node[a]['state'] = random.randint(i, i+1)
                if (neighbor_avg - i) == -0.5:
                    nextg._node[a]['state'] = random.randint(i-1, i)
                
            seeker_value = seeker_value + nextg._node[a]['state']
            nextg._node[a]['payoff'] = base_pay - (true - nextg._node[a]['state'])**2
        
        seeker_avg = seeker_value/seeker_total
        
        if g._node[a]['influencer'] == 1: # if influencer
            nextg._node[a]['payoff'] = base_pay - (seeker_avg - nextg._node[a]['state'])**2   
        
            nextg._node[a]['influencer'] = 1
            nextg._node[a]['state'] = g._node[a]['state']
            
        
        if g._node[a]['state'] == 1:
            curprev += 1
            
    g = deepcopy(nextg)
    prevalence.append(curprev/len(g.nodes))

def observe():
    global g, prevalence
    cla()
    nx.draw_networkx(g, cmap = 'Wistia', vmin = 0, vmax = 1, 
            #labels = labels, fontcolor = "whitesmoke", font_size = 20,        
            node_color = [g._node[i]['state'] for i in g.nodes],
            pos = g.pos)

    
#pycxsimulator.GUI().start(func = [initialize, update, observe])

# Update Prevalence Array
for i in range(0,simulations):    # loop over all simulations
    initialize()                  # initialize each simulation
    for j in range(1,timesteps):  # loop over the timesteps for that simulation
        update()                  # update
    print("The current simulation being run is: %d " % (i + 1))
    print("The true value for this simulation is: {}".format(true))
    print()
    prevalence_array[:,i] = prevalence         # store the resulting simulation in prevalence_array

# Graph Prevalence
prevalence_avg = prevalence_array.mean(axis=1)  # takes row average

plt.scatter(range(len(prevalence_avg)), prevalence_avg, alpha=0.1)
plt.xlabel("Time")
plt.ylabel("Prevalence of Influencer Signal")
plt.show()
plt.savefig('plot%d.png' % i)
    
