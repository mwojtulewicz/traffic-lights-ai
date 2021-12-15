from abc import abstractmethod
from typing import List
import keyboard
import tqdm
import traci
import numpy as np
import importlib
import matplotlib.pyplot as plt
import seaborn as sn
import pandas as pd

from rewards import NegQueueReward, get_metrics_tuple
from states import QueueState

envs = importlib.import_module('traffic_envs')
# states = importlib.import_module('states')
# rewards = importlib.import_module('rewards')


class Baseline_Agent:
    """ baseline agent interface for comparing trained agents performance """
    def __init__(self, **kw):
        pass

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def observe(self, state):
        pass

    @abstractmethod
    def act(self) -> int:
        pass

    def __str__(self) -> str:
        return 'Baseline_Agent\n'


class Alternating_Phases(Baseline_Agent):
    """
    agent alternates traffic lights with preset length
    """
    
    def __init__(self, phases_durations: List[int]):
        
        self._phases_durations = phases_durations
        
        self.reset()
        
    def reset(self):
        self._current_phase = 0
        self._current_phase_time = 0
    
    def observe(self, _state):
        self._current_phase_time += 1
    
    def act(self) -> int:
        if self._current_phase_time > self._phases_durations[self._current_phase]:
            self._current_phase = (self._current_phase + 1) % 4
            self._current_phase_time = 0
        return self._current_phase
    
    def __str__(self) -> str:
        return super().__str__() + 'Alternating Phases Strategy \n'
    
    
def test_baseline_agent(env_class: str, agent_class: Baseline_Agent, env_params: dict, agent_params: dict, metric_classes: list = [],
                        max_timesteps: int = 10000, gui: bool = False, verbose: bool = False, verbose_freq: int = 10, 
                        summary: bool = False, show: bool = False, **kwargs):
    
    env_class = getattr(envs, env_class)
    env = env_class(**{**env_params, "max_steps":max_timesteps, "gui": gui})
    
    agent = agent_class(**agent_params)
    
    avg_reward = 0
    rewards = []
    
    metrics = {m(): [] for m in metric_classes}
    
    s_t = env.reset()
    
    iterator = tqdm.trange(int(max_timesteps), leave=True, position=0)
    for t in iterator:

        agent.observe(s_t)
        action = agent.act()
        s_t, r_t, _done, _info_dict = env.step(action)
        
        avg_reward = (avg_reward * t + r_t) / (t + 1)
        rewards.append(r_t)
        for metric, values in metrics.items():
            values.append(metric.calculate())

        if verbose and t%verbose_freq==0: 
            tqdm.tqdm.write(f" - {t} -- {r_t = } -- {avg_reward = :.2f}")

        if _done:
            s_t = env.reset()
            if verbose: tqdm.tqdm.write('termination, restarting...')

        # if keyboard.is_pressed('esc'):
        #     iterator.close()
        #     print('closed')
        #     break
    
    
    if summary:
        
        print(f"\n{agent.__class__.__name__} baseline agent performance summary:")
        print(f" - {avg_reward = :.4f} ")
        for metric, values in metrics.items():
            print(f" - metric: {metric.__class__.__name__:16s} -- avg: {np.mean(values):.4f} -- std: {np.std(values):.4f}")
        print()
        
        if show:
            
            for metric, values in metrics.items():
                plt.figure(figsize=(16, 8.2))
                sn.histplot(values, discrete=True, kde=True)
                plt.title(f'{metric.__class__.__name__} values distribution')
                plt.ylabel('Count')
                plt.xlabel('Value')
                plt.tight_layout()
            
            plt.figure(figsize=(16,8.2))
            sn.histplot(rewards, discrete=True, kde=True)
            plt.title('Reward values distribution')
            plt.ylabel('Count')
            plt.xlabel('Value')
            plt.tight_layout()
            
            plt.show()
        
        env.close()
        
        summary = [f"BL_{agent.__class__.__name__}", "-", "-"] + [np.mean(values) for values in metrics.values()]
        columns = ["id", "state_class", "reward_class"] + [f"{metric.__class__.__name__} (mean)" for metric in metrics.keys()]
        
        return pd.DataFrame.from_records([summary], columns=columns)
        
    env.close()



if __name__=='__main__':
    
    agent_class = Alternating_Phases
    env_class = 'Environment_Traffic_Lights'
    
    env_params = {
        "route_car_freq": [0.02, 0.05, 0.01]*4,
        "yellow_duration": 4,
        "green_duration": 4,
        "state_class": QueueState,
        "reward_class": NegQueueReward
    }
    
    agent_params = {
        "phases_durations": [7, 3, 7, 3]
    }
    
    df = test_baseline_agent(env_class=env_class, agent_class=agent_class, 
                             env_params=env_params, agent_params=agent_params, 
                             max_timesteps=500, verbose=True, verbose_freq=50, gui=False, 
                             summary=True, show=True, metric_classes=get_metrics_tuple())
    
    print(df)
    
