import numpy as np
import torch
import torch.nn as nn
from typing import Union
from pathlib import Path
import json, time, keyboard, tqdm, sys
import matplotlib.pyplot as plt
import seaborn as sn
import importlib

envs = importlib.import_module('traffic_envs')
models = importlib.import_module('models')
states = importlib.import_module('states')
rewards = importlib.import_module('rewards')


class Agent:
    """
    universal agent interface for loading and testing trained agents
    """
    def __init__(self, model_dir : Union[str, Path]):
        if not isinstance(model_dir, Path):
            model_dir = Path(model_dir)
        self._DIR = model_dir
        
        with open(model_dir / 'hiperparams.json') as hpf:
            self._hp = json.load(hpf)
        
        self._ENV_CLASS_NAME = self._hp.get('environment', None)
        self._ENV_CLASS = getattr(envs, self._ENV_CLASS_NAME)
        
        self._STATE_CLASS = getattr(states, self._hp['state_class'])
        self._REWARD_CLASS = getattr(rewards, self._hp['reward_class'])
        
        self._MODEL_CLASS = getattr(models, self._hp['model']['name'])
        self._MODEL = self._MODEL_CLASS(**self._hp['model'])
        self.load_last_checkpoint()
        
        self._observed_state = None
        
    def observe(self, state):
        self._observed_state = state
        
    def act(self):
        with torch.no_grad():
            action = torch.argmax(self._MODEL(torch.Tensor(self._observed_state)))
            return action
    
    def load_checkpoint(self, episode:int):
        if (self._DIR / 'checkpoints' / f'ep{episode}.pt').exists():
            self._MODEL.load_state_dict(torch.load(self._DIR / 'checkpoints' / f'ep{episode}.pt'))
    
    def load_checkpoint_file(self, filename:Union[str,Path]):
        if Path(filename).exists:
            self._MODEL.load_state_dict(torch.load(filename))
    
    def load_last_checkpoint(self):
        self._MODEL.load_state_dict(torch.load(list((self._DIR / 'checkpoints').iterdir())[-1]))
    
    def build_environment(self, **kwargs):
        """ note that provided kwargs have higher priotity """
        kw = {**self._hp, "state_class":self._STATE_CLASS, "reward_class":self._REWARD_CLASS, **kwargs}
        return self._ENV_CLASS(**kw)

    def hiperparams(self):
        return self._hp
    
    
    
def test_agent(model_dir: Union[str,Path], checkpoint_episode: Union[int,str] = -1, max_timesteps: int = 1000, 
               gui: bool = True, verbose: bool = True, verbose_freq: int = 10, metrics: list = [],
               **kwargs):
    
    # TODO: metrics
    
    agent = Agent(model_dir)
    
    environment = agent.build_environment(gui=gui, **kwargs)

    if isinstance(checkpoint_episode, int):
        agent.load_checkpoint(checkpoint_episode)
    elif isinstance(checkpoint_episode, str):
        agent.load_checkpoint_file(checkpoint_episode)

    avg_reward = 0
    rewards = []

    s_t = environment.reset()

    iterator = tqdm.trange(int(max_timesteps), leave=True, position=0)
    for t in iterator:

        agent.observe(s_t)
        action = agent.act()
        s_t, r_t, _done, _info_dict = environment.step(action)

        avg_reward = (avg_reward * t + r_t) / (t + 1)
        rewards.append(r_t)
        if verbose and t%verbose_freq==0: 
            tqdm.tqdm.write(f" - {t} -- {r_t = } -- {avg_reward = :.2f}")

        if _done:
            s_t = environment.reset()
            if verbose: tqdm.tqdm.write('termination, restarting...')

        if keyboard.is_pressed('esc'):
            iterator.close()
            print('closed')
            break

    print(f'\n{avg_reward = :.4f}\n')

    plt.figure(figsize=(16,8.2))
    sn.histplot(rewards, discrete=True, kde=True)
    plt.title('Reward value distribution')
    plt.ylabel('Count')
    plt.xlabel('Value')
    plt.tight_layout()
    plt.show()
    
    environment.close()
    
    
    
if __name__=="__main__":
    
    MODEL_DIR = "models/environment_traffic_lights/1638899442"
    
    test_agent(model_dir=MODEL_DIR)
    