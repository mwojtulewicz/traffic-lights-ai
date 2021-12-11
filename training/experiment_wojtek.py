import numpy as np
from itertools import product
import matplotlib.pyplot as plt
from pathlib import Path
import tqdm
import time
import keyboard, json
import torch
import torch.nn as nn
from torch.utils.tensorboard import SummaryWriter

from traffic_envs import Environment_Traffic_Lights
from states import get_states_tuple
from rewards import get_rewards_tuple
from memory import ReplayBuffer
from models import DQN_3h

# static env parameters
MAX_STEPS = 10000
ROUTE_CAR_FREQ = [0.02, 0.05, 0.01]*4  # right, straight, left - for 4 starting nodes
NET_DIR = 'intersection/'
SUMO_CFG_FILE = NET_DIR + 'my_net.sumocfg'
ROUTE_FILE = NET_DIR + 'my_net.rou.xml'
GUI = False
YELLOW_DURATION = 4
GREEN_DURATION = 4


# training parameters for one state,reward pair
NUM_EPISODES = 125
MAX_TIMESTEPS = MAX_STEPS

MIN_BUFFER_LENGTH = 10000
MAX_BUFFER_LENGTH = 50000
TRAIN_FREQ = 10
BATCH_SIZE = 32

HIDDEN_LAYERS = [128,32,8]
OPTIMIZER_LR = 0.0008

TARGET_NET_UPDATE_FREQ = 2500
QNET_CHECKPOINT_FREQ = 25

GAMMA = 0.99
MAX_EPS = 1
MIN_EPS = 0.1
EPS_DECAY = 0.01

STATE_SHAPE = 4*4
NUM_ACTIONS = 4

DEVICE = 'cpu'

# -----------------------------------------------------------------------------------------

STATES = get_states_tuple(who="Wojtek")
REWARDS = get_rewards_tuple(who="Wojtek")

num_experiments = len(STATES) * len(REWARDS)

for experiment_number, (state_class, reward_class) in enumerate(product(STATES, REWARDS)):

    env = Environment_Traffic_Lights(state_class=state_class, reward_class=reward_class, max_steps=MAX_STEPS,
                                    route_car_freq=ROUTE_CAR_FREQ, sumo_cfg_file=SUMO_CFG_FILE, route_file=ROUTE_FILE,
                                    gui=GUI, yellow_duration=YELLOW_DURATION, green_duration=GREEN_DURATION)

    START_TIME = int(time.time())

    MODEL_DIR = Path(f'models/{env.__class__.__name__.lower()}/{START_TIME}')
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    (MODEL_DIR / 'checkpoints').mkdir(parents=True, exist_ok=True)

    Qnet = DQN_3h(input_size=STATE_SHAPE, hidden_sizes=HIDDEN_LAYERS, output_size=NUM_ACTIONS).to(DEVICE)
    # Qtarget = DQN_3h(input_size=STATE_SHAPE, hidden_sizes=HIDDEN_LAYERS, output_size=NUM_ACTIONS).to(DEVICE)
    # Qtarget.load_state_dict(Qnet.state_dict())

    optimizer = torch.optim.Adam(Qnet.parameters(), lr=OPTIMIZER_LR)
    loss = nn.HuberLoss()

    env_hiperparams = env.hiperparams()
    learning_hiperparams = {
        'environment': env.__class__.__name__,
        'learning_method': 'Deep Q-Learning with Replay Buffer',
        'num_episodes': NUM_EPISODES,
        'max_timesteps': MAX_TIMESTEPS,
        'min_buffer_lenth': MIN_BUFFER_LENGTH,
        'max_buffer_length': MAX_BUFFER_LENGTH,
        'train_freq': TRAIN_FREQ,
        'batch_size': BATCH_SIZE,
        'target_net_update_freq': TARGET_NET_UPDATE_FREQ,
        'gamma': GAMMA,
        'max_epsilon': MAX_EPS,
        'min_epsilon': MIN_EPS,
        'epsilon_decay': EPS_DECAY,
        'device': DEVICE
    }
    hiperparams = {**env_hiperparams, **learning_hiperparams}
    hiperparams['model'] = Qnet.hiperparams()
    hiperparams['optimizer'] = {'name': optimizer.__class__.__name__, 'state_dict':optimizer.state_dict()}
    hiperparams['loss'] = loss.__class__.__name__
    with open(MODEL_DIR / 'hiperparams.json', 'w') as f:
        json.dump(hiperparams, f, indent=2)

    writer = SummaryWriter(log_dir=f'../runs/{env.__class__.__name__}/run{START_TIME}_experiment{experiment_number+1}', comment=f'{START_TIME}')

    # -------------------------------------------------------------------------------------

    replay_buffer = ReplayBuffer(MAX_BUFFER_LENGTH, device=DEVICE)

    avg_episode_loss_arr = np.zeros(shape=NUM_EPISODES)
    avg_episode_reward_arr = np.zeros(shape=NUM_EPISODES)

    for episode in range(0,NUM_EPISODES):

        epsilon = max(MAX_EPS - (episode)*EPS_DECAY, MIN_EPS)
        print(f'\nEPISODE: {episode+1:3d} of {NUM_EPISODES} --> {epsilon = :.2f}      ---      experiment {experiment_number+1} of {num_experiments} --> state: {state_class.desc()}, reward: {reward_class.desc()}')
        
        s_t = np.array(env.reset())

        episode_rewards = np.zeros(shape=MAX_TIMESTEPS)
        episode_losses = np.zeros(shape=int(np.ceil(MAX_TIMESTEPS/TRAIN_FREQ)))
        loss_idx = 0

        for t in tqdm.trange(MAX_TIMESTEPS, position=0, leave=True):
        
            optimizer.zero_grad()

            with torch.no_grad():
                if np.random.rand() <= epsilon:
                    action = np.random.choice(NUM_ACTIONS)
                else:
                    action = torch.argmax(Qnet(torch.Tensor(s_t).to(DEVICE)), dim=0).item()

            s_t1, r_t, done, info = env.step(action)
            s_t1 = np.array(s_t1)
            exp_tuple = (s_t, action, r_t, s_t1, done)
            replay_buffer.append(exp_tuple)

            # if VERBOSE and t%VERBOSE_FREQ==0:
            #     a = ACTION_LUT[action]
            #     print(f' | {t=:4d} - {a=:>4s} - {s_t=} - {r_t=} - {Qtable[s_t]=}')

            if len(replay_buffer)>MIN_BUFFER_LENGTH and t%TRAIN_FREQ==0:
                _states, _actions, _rewards, _next_states, _dones = replay_buffer.sample(size=BATCH_SIZE)

                _qvalues_all = Qnet(_states)
                _qvalues_actions = _qvalues_all[np.arange(BATCH_SIZE), _actions]
                
                with torch.no_grad():
                    _qvalues_next_all = Qnet(_next_states)  # NOTE: in DDQL there would be Qtarget
                    _qvalues_next_max = torch.max(_qvalues_next_all, axis=1)[0]
                    _qvalues_next_max[_dones] = 0

                    _qvalues_expected = _rewards + GAMMA * _qvalues_next_max
                
                _loss = loss(_qvalues_expected, _qvalues_actions)
                _loss.backward()
                optimizer.step()
                
                episode_losses[loss_idx] = _loss.detach().cpu()
                loss_idx += 1
            
            # if t%TARGET_NET_UPDATE_FREQ==0:
            #     Qtarget.load_state_dict(Qnet.state_dict())

            episode_rewards[t] = r_t
            
            if done:
                s_t = np.array(env.reset())
            else:
                s_t = s_t1


        avg_episode_loss = np.average(episode_losses)
        avg_episode_loss_arr[episode] = avg_episode_loss

        avg_episode_reward = np.average(episode_rewards)
        avg_episode_reward_arr[episode] = avg_episode_reward

        writer.add_scalar(tag='avg_episode_loss', scalar_value=avg_episode_loss, global_step=episode)
        writer.add_scalar(tag='avg_reward', scalar_value=avg_episode_reward, global_step=episode)
        writer.add_scalar(tag='epsilon', scalar_value=epsilon, global_step=episode)

        if (episode+1)%QNET_CHECKPOINT_FREQ==0:
            torch.save(Qnet.state_dict(), MODEL_DIR / 'checkpoints' / f'ep{episode+1:05d}.pt')

        print(f' --- {avg_episode_loss = :.4f} -- {avg_episode_reward = :.2f}')

        if keyboard.is_pressed('ctrl+space+1'):
            print(f'training interrupted after {episode+1} episode, saving...')
            torch.save(Qnet.state_dict(), MODEL_DIR / 'checkpoints' / f'ep{episode+1:05d}.pt')
            break

    env.close()

    # saving

    plt.figure(figsize=(16,8.2))
    plt.title('Average episode loss'); plt.xlabel('Episode number'); plt.ylabel('Value'), plt.grid()
    plt.plot(avg_episode_loss_arr)
    plt.tight_layout()
    plt.savefig(MODEL_DIR/'avg_episode_loss.png')

    plt.figure(figsize=(16,8.2))
    plt.title('Average episode reward'); plt.xlabel('Episode number'); plt.ylabel('Value'), plt.grid()
    plt.plot(avg_episode_reward_arr)
    plt.tight_layout()
    plt.savefig(MODEL_DIR/'avg_episode_reward.png')

    np.save(MODEL_DIR / 'avg_episode_loss.npy', avg_episode_loss_arr)
    np.save(MODEL_DIR / 'avg_episode_reward.npy', avg_episode_reward_arr)
    torch.save(Qnet.state_dict(), MODEL_DIR / 'checkpoints' / 'final.pt')  # earlier Qnet only

    hiperparams["learning_duration[s]"] = int(time.time()) - START_TIME
    with open(MODEL_DIR / 'hiperparams.json', 'w') as f:
        json.dump(hiperparams, f, indent=2)

    print(f'learning duration: {hiperparams["learning_duration[s]"]} [s]')
    # plt.show()

