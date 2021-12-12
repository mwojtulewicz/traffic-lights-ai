import os
import sys
import traci

import src.config as config
import src.environment as environment
import src.agent as agent
import src.states as states
import src.rewards as rewards
import src.plotting as plotting

if __name__ == '__main__':
    os.environ['SUMO_HOME'] = '/usr/share/sumo/'
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)

    state_class = states.CountState
    reward_class = rewards.ThroughputReward
    env = environment.Environment(state_class, reward_class)
    agent = agent.Agent()

    mean_rewards = []
    mean_throughput = []
    mean_queue_len = []

    for episode in range(config.NUM_EPISODES):
        # logging
        cum_reward = 0
        cum_throughput = 0
        cum_queue_len = 0

        epsilon = 1.0 - (episode / config.NUM_EPISODES)
        old_state = env.reset()

        for i in range(config.MAX_STEPS // config.READ_EVERY):
            action = agent.act(old_state, epsilon)
            new_state, reward, done, info = env.step(action)

            cum_reward += reward
            cum_throughput += info['throughput']
            cum_queue_len += info['queue_len']

            if config.TRAIN_MODE:
                agent.memory.add_sample((old_state, action, reward, new_state))
            
            if done and config.TRAIN_MODE:
                break

        traci.close() # TODO: move to Environment

        mean_rewards.append(cum_reward/i)
        mean_throughput.append(cum_throughput/i)
        mean_queue_len.append(cum_queue_len/i)

        if config.TRAIN_MODE:
            agent.train()

    if config.TRAIN_MODE:
        # model saving
        agent.save_model()

        # visualization
        plotting.save_plots(mean_rewards, mean_throughput, mean_queue_len)



