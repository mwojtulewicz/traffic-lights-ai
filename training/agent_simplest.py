import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import tqdm
import time

from traffic_envs import Environment_NS_Only
from memory import ReplayBuffer

# ------------------------------------------------------------------------------------------------------------

# env variables
NET_DIR = 'intersection/'
SUMO_CFG_FILE = NET_DIR + 'my_net.sumocfg'
ROUTE_FILE = NET_DIR + 'my_net.rou.xml'
MAX_STEPS = 1000
GUI = False

# training parameters
NUM_EPISODES = 100
MAX_TIMESTEPS = MAX_STEPS

MIN_BUFFER_LENGTH = 500
MAX_BUFFER_LENGTH = 5000
TRAIN_FREQ = 10
BATCH_SIZE = 32

LR = 0.5
GAMMA = 0.99
MAX_EPS = 1
MIN_EPS = 0.05
EPS_DECAY = 0.05

STATE_SHAPE = [1]
NUM_ACTIONS = 2
QT_SHAPE = STATE_SHAPE + [NUM_ACTIONS]

DEVICE = None

START_TIME = int(time.time())

# ------------------------------------------------------------------------------------------------------------

env = Environment_NS_Only(sumo_cfg_file=SUMO_CFG_FILE, route_file=ROUTE_FILE, max_steps=MAX_STEPS, gui=GUI)
MODEL_DIR = Path(f'models/{env.__class__.__name__.lower()}/{START_TIME}')
MODEL_DIR.mkdir(parents=True, exist_ok=True)

Qtable = np.zeros(shape=QT_SHAPE)

replay_buffer = ReplayBuffer(max_length=MAX_BUFFER_LENGTH, device=DEVICE)

# ------------------------------------------------------------------------------------------------------------

avg_episode_rewards_arr = np.zeros(shape=NUM_EPISODES)

for episode in range(NUM_EPISODES):
    
    epsilon = max(MAX_EPS - (episode+1)*EPS_DECAY, MIN_EPS)
    print(f'\nEPISODE: {episode+1:3d} of {NUM_EPISODES} --> {epsilon = :.2f}')

    episode_rewards = np.zeros(shape=MAX_TIMESTEPS)

    s_t = env.reset()

    for t in tqdm.trange(MAX_TIMESTEPS, position=0, leave=True):

        if np.random.rand() <= epsilon:
            action = np.random.choice(NUM_ACTIONS)
        else:
            action = np.argmax(Qtable[s_t])
        
        s_t1, r_t, done, info = env.step(action)

        exp_tuple = (s_t, action, r_t, s_t1, done)
        replay_buffer.append(exp_tuple)

        if len(replay_buffer)>=MIN_BUFFER_LENGTH and t%TRAIN_FREQ==0:
            # _states, _actions, _rewards, _next_states, _dones = replay_buffer.sample(size=BATCH_SIZE)
            exp_indicies = np.random.choice(len(replay_buffer), size=BATCH_SIZE)

            for i in exp_indicies:
                _st, _a, _rt, _st1, _done = replay_buffer[i]
                # print(_st, _a, _rt, _st1, _done)
                # print(Qtable[_st])
                TD = _rt - Qtable[_st][_a]
                if not _done:
                    TD += GAMMA * np.max(Qtable[_st1])
                Qtable[_st][_a] += LR * TD
            
        if done:
            s_t = env.reset()
        else:
            s_t = s_t1
        
        episode_rewards[t] = r_t

    
    avg_episode_reward = episode_rewards.mean()
    avg_episode_rewards_arr[episode] = avg_episode_reward
    print(f' --- {avg_episode_reward = :.6f}')

env.close()

# ------------------------------------------------------------------------------------------------------------
# saving

plt.figure(figsize=(12,6.5))
plt.title('Average episode reward'); plt.xlabel('Episode number'); plt.ylabel('Value'), plt.grid()
plt.plot(avg_episode_rewards_arr)
plt.tight_layout()
plt.savefig(MODEL_DIR/'avg_episode_reward.png')

np.save(MODEL_DIR / 'Qtable.npy', Qtable)

plt.show()
