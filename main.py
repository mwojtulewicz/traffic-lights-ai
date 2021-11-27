import os
import sys

import matplotlib.pyplot as plt

import traci
from sumolib import checkBinary

import src.config as config
import src.environment as environment
import src.agent as agent

if __name__ == '__main__':
    os.environ['SUMO_HOME'] = '/usr/share/sumo/'
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
    sumo_binary = checkBinary('sumo-gui')
    
    env = environment.Environment(sumo_binary)
    agent = agent.Agent()
    mean_rewards = []

    for episode in range(10):
        epsilon = 1.0 - (episode / config.NUM_EPISODES)
        cum_reward = 0
        old_state = env.reset()

        for i in range(config.MAX_STEPS):
            action = agent.act(old_state, epsilon)
            new_state, reward, done, _ = env.step(action)
            cum_reward += reward

            agent.memory.add_sample((old_state, action, reward, new_state))
            
            if done:
                break

        traci.close() # TODO: move to Environment
        mean_rewards.append(cum_reward/i)
        # agent.train()

    # zapis wizualizacji
    plt.style.use('seaborn')
    plt.plot(mean_rewards)
    plt.xlabel('Episodes')
    plt.ylabel('Mean reward')
    plt.savefig('./figures/rewards.png')



