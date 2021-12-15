from pathlib import Path
import numpy as np
import pandas as pd

from baseline_agent import Alternating_Phases, test_baseline_agent
from agent_testing import models_summaries
from rewards import NegQueueReward, get_metrics_tuple
from states import QueueState


def test_baseline(timesteps: int = 1000):
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
    
    np.random.seed(0)
    df = test_baseline_agent(env_class=env_class, agent_class=agent_class, 
                             env_params=env_params, agent_params=agent_params, 
                             max_timesteps=timesteps, verbose=False, verbose_freq=50, gui=False, 
                             summary=True, show=False, metric_classes=get_metrics_tuple())
    
    return df    


def test_models(timesteps: int = 1000): 
    test_models_dir = Path("models/environment_traffic_lights")
    
    df = models_summaries(models_dir=test_models_dir, timesteps=timesteps, seed=0)

    return df


if __name__=="__main__":
    
    TIMESTEPS = 1000
    
    baseline_df = test_baseline(TIMESTEPS)
    models_df = test_models(TIMESTEPS)
    
    df = pd.concat([models_df, baseline_df], ignore_index=True)
    
    df.to_excel("models/environment_traffic_lights/evaluation.xlsx")
