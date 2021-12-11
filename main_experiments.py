import os
import sys
import traci
import itertools

from src.environment import Environment
from src.agent import Agent
from src.states import get_states_tuple
from src.rewards import get_rewards_tuple

import src.config as config
import src.plotting as plotting

if __name__ == '__main__':
    os.environ['SUMO_HOME'] = '/usr/share/sumo/'
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)

    f = open('./logs/experiments.txt', 'w')

    states = get_states_tuple()
    rewards = get_rewards_tuple()
    pairs = [[(state, reward) for state in states] for reward in rewards]
    pairs = tuple(itertools.chain(*pairs))
    
    for exp_idx, (state_class, reward_class) in enumerate(pairs):
        f.write(f'=== Experiment {exp_idx} ===\n')
        f.write(f'State: {state_class.desc()}\n')
        f.write(f'Reward: {reward_class.desc()}\n\n')
        
        env = Environment(state_class, reward_class)
        agent = Agent()

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

                agent.memory.add_sample((old_state, action, reward, new_state))
                
                if done:
                    break

            traci.close() # TODO: move to Environment

            mean_rewards.append(cum_reward/i)
            mean_throughput.append(cum_throughput/i)
            mean_queue_len.append(cum_queue_len/i)

            agent.train()

        # model saving
        # agent.save_model() # TODO: nazwa

        # visualization
        plotting.save_plots(mean_rewards, mean_throughput, mean_queue_len, prefix=f'{exp_idx}_')

    f.close()
