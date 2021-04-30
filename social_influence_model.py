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
simulations = 20

# Track prevalence of influencer signal
prevalence_array = np.zeros([timesteps, simulations])

# Track influencer payoffs
influencer_array = np.zeros([timesteps, simulations])

# Track seeker payoffs en masse
seeker_array = np.zeros([timesteps, simulations]) 

N = 10 # number of nodes
k = 2 # number of connected neighbors for Neumann-Watts-Strogatz network
p = 0.2 # probability of rewiring edges for Neumann-Watts-Strogatz network
seed = 150 # seed value

# Signals initially assigned to nodes
likert = 5

# Base pay provided to each node initially
base_pay = 16


def initialize():
    global g, nextg, prevalence, true, influencer_pay, seeker_pay
    
    prevalence = []
    influencer_pay = []
    seeker_pay = []
    
    #g = nx.complete_graph(N) # use complete graph
    g = nx.newman_watts_strogatz_graph(N,k,p,seed) # use newman-watts-strogatz network
    g.pos = nx.spring_layout(g) # create initial position for nodes
    
    # Each node gets an attribute, state, which tracks each node's signal
    nx.set_node_attributes(g, 0, 'state')
    for n in g.nodes:
        g._node[n]['state'] = random.randint(0, likert - 1)
    g._node[0]['state'] = random.randint(round((likert - 1)/2), likert - 1)
    
    # Each node gets an attribute, influencer, where 1 := influencer and 0 := seeker
    nx.set_node_attributes(g, 0, 'influencer')
    g._node[0]['influencer'] = 1 # node 0 is the influencer
    
    # Each node gets an attribute, payoff, which track's each node's payoffs
    nx.set_node_attributes(g, 0, 'payoff')
    true = 0
    for m in g.nodes:
        g._node[m]['payoff'] = base_pay # all nodes start with base pay
        if g._node[m]['influencer'] == 0:
            true = true + g._node[m]['state']
    true = true/(N-1) # true signal, defined as average of seekers' initial signals
    
    nextg = g.copy()
    nextg.pos = g.pos
    prevalence.append(1/len(g.nodes)) # consider the initial prevalence of the influencer signal to be just 1/total
    influencer_pay.append(base_pay) # influnecer payoff array starts with base pay
    seeker_pay.append(base_pay) # seeker payoff array starts with base pay

def update():
    global g, nextg, prevalence, true, influencer_pay, seeker_pay
    curprev = 0 # track prevalence of influencer signal within update function
    nextg = deepcopy(g) # current and next time steps are totally separate
    
    seeker_value = 0
    seeker_total = N-1 # total number of seekers
    seeker_avg = 0
        
    neighbor_value = 0
    neighbor_total = 0 # total number of neighbors
    neighbor_avg = 0
        
    seeker_payoff = 0
    influencer_payoff = 0
        
    for a in g.nodes:
        
        for b in g.neighbors(a):
            neighbor_value = neighbor_value + g._node[b]['state']
            neighbor_total += 1
        neighbor_avg = neighbor_value/neighbor_total # average signal of neighbors, i.e., DeGroot processing
        
        
        if g._node[a]['influencer'] == 0: # if seeker
            nextg._node[a]['influencer'] = 0 # remain seeker
            
            seeker_payoff = g._node[a]['payoff']
            
            for i in range(0, likert): # define the next signal for seekers after DeGroot processing
                
                if abs(neighbor_avg - i) < 0.5:
                    nextg._node[a]['state'] = i
                if (neighbor_avg - i) == 0.5:
                    nextg._node[a]['state'] = random.randint(i, i+1)
                if (neighbor_avg - i) == -0.5:
                    nextg._node[a]['state'] = random.randint(i-1, i)
                
            seeker_value = seeker_value + nextg._node[a]['state']
            nextg._node[a]['payoff'] = base_pay - (true - g._node[a]['state'])**2 # payoff function for seekers
            seeker_payoff = seeker_payoff + nextg._node[a]['payoff'] # total value of seeker payoffs
        
        seeker_payoff = seeker_payoff/seeker_total # average per-seeker payoff
        seeker_avg = seeker_value/seeker_total # average per-seeker signal, used to calculate influencer's payoff
        
        # print('Seeker payoff is: {}'.format(seeker_payoff))
        # print('Seeker avg is: {}'.format(seeker_avg))
        
        if g._node[a]['influencer'] == 1: # if influencer
            nextg._node[a]['influencer'] = 1 # remain influencer
            nextg._node[a]['state'] = g._node[a]['state'] # influencer keeps same signal across rounds   
        
            influencer_state = g._node[a]['state']   # store influencer's signal
            influencer_payoff = g._node[a]['payoff'] # store influencer's payoff

            nextg._node[a]['payoff'] = base_pay - (seeker_avg - g._node[a]['state'])**2 # payoff function for influencers  
            
            influencer_payoff = nextg._node[a]['payoff']
            # print('Influencer payoff is: {}'.format(influencer_payoff))
        
        if g._node[a]['state'] == influencer_state:
            curprev += 1
            
    g = deepcopy(nextg)
    prevalence.append(curprev/len(g.nodes))
    influencer_pay.append(influencer_payoff)
    seeker_pay.append(seeker_payoff)

def observe():
    global g, prevalence
    cla()
    nx.draw_networkx(g, cmap = cm.Wistia, vmin = 0, vmax = 1, 
            node_color = [g._node[i]['influencer'] for i in g.nodes],
            pos = g.pos, font_color = 'white')

    
#pycxsimulator.GUI().start(func = [initialize, update, observe])

# Update Prevalence Array
for i in range(0,simulations):    # loop over all simulations
    initialize()                  # initialize each simulation
    
    if i == 0: # draw first simulation's initial network with signals  
        labels = {}    
        for j in g.nodes:
            labels[j] = g._node[j]['state']
        
        nx.draw_networkx(g, vmin = 0, vmax = 1, cmap = cm.bwr,
            node_color = [g._node[j]['influencer'] for j in g.nodes],
            pos = g.pos, font_color = 'white',
            labels = labels)
        plt.show()
        
    for j in range(1,timesteps):  # loop over the timesteps for that simulation
        update()                  # update
        
    print("The current simulation being run is: %d " % (i + 1))
    print("The true value for this simulation is: {}".format(true))
    print()
    
    prevalence_array[:,i] = prevalence         # store the resulting simulation in prevalence_array
    influencer_array[:,i] = influencer_pay     # store the resulting simulation in influencer_array
    seeker_array[:,i] = seeker_pay             # store the resulting simulation in seeker_array

prevalence_avg = prevalence_array.mean(axis=1)  # take row average
influencer_avg = influencer_array.mean(axis=1)  # take row average
seeker_avg = seeker_array.mean(axis=1)          # take row average

# Graph Prevalence
for i in range(0,simulations):
    prevalence_graph = scatter(range(len(prevalence_array[:,i])), prevalence_array[:,i], alpha = 0.05)
    plot(range(len(prevalence_array[:,i])), prevalence_array[:,i], alpha = 0.05)    
scatter(range(len(prevalence_avg)), prevalence_avg, color = 'black', alpha = 1)
plot(range(len(prevalence_avg)), prevalence_avg, color = 'black', alpha = 1)
autoscale(enable=True, axis='both')
title("Prevalence of Influencer Signal")
xlabel("Time")
ylabel("Prevalence (Fraction of Total Nodes)")
show(prevalence_graph)

# Graph Influencer Payoff
for i in range(0,simulations):
    influencer_graph = scatter(range(len(influencer_array[:,i])), influencer_array[:,i], alpha = 0.05)
    plot(range(len(influencer_array[:,i])), influencer_array[:,i], alpha = 0.05)
scatter(range(len(influencer_avg)), influencer_avg, color = 'black', alpha = 1)
plot(range(len(influencer_avg)), influencer_avg, color = 'black', alpha = 1)
autoscale(enable=True, axis='both')
title("Average Payoffs for an Influencer")
xlabel("Time")
ylabel("Payoffs ($)")
show(influencer_graph)

# Graph Seeker Payoff
for i in range(0,simulations):
    seeker_graph = scatter(range(len(seeker_array[:,i])), seeker_array[:,i], alpha = 0.05)
    plot(range(len(seeker_array[:,i])), seeker_array[:,i], alpha = 0.05)
scatter(range(len(seeker_avg)), seeker_avg, color = 'black', alpha = 1)
plot(range(len(seeker_avg)), seeker_avg, color = 'black', alpha = 1)
autoscale(enable=True, axis='both')
title("Average Payoffs for a Seeker")
xlabel("Time")
ylabel("Payoffs ($)")
show(seeker_graph)
