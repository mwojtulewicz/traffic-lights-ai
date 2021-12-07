import os
import sys

import matplotlib.pyplot as plt

import traci

import src.config as config
import src.environment as environment
import src.agent as agent
import src.states as states
import src.rewards as rewards

if __name__ == '__main__':
    os.environ['SUMO_HOME'] = '/usr/share/sumo/'
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
    
    state_class = states.CountState
    reward_class = rewards.WaitDiffReward
    env = environment.Environment(state_class, reward_class)
    agent = agent.Agent()
    mean_rewards = []

    for episode in range(config.NUM_EPISODES):
        epsilon = 1.0 - (episode / config.NUM_EPISODES)
        cum_reward = 0
        old_state = env.reset()

        for i in range(config.MAX_STEPS):
            action = agent.act(old_state, epsilon)
            new_state, reward, done, _ = env.step(action)
            cum_reward += reward

            if config.TRAIN_MODE:
                agent.memory.add_sample((old_state, action, reward, new_state))
            
            if done:
                break

        traci.close() # TODO: move to Environment
        mean_rewards.append(cum_reward/i)

        if config.TRAIN_MODE:
            agent.train()

    if config.TRAIN_MODE:
        # model saving
        agent.save_model()

        # visualization
        plt.style.use('seaborn')
        plt.plot(mean_rewards)
        plt.xlabel('Episodes')
        plt.ylabel('Mean reward')
        plt.savefig('./figures/rewards.png')



