import numpy as np
import traci
import sys, os
from sumolib import checkBinary
from typing import List, Union, Tuple

from generator import TrafficGenerator
from rewards import *
from states import *

def sumo_init(sumo_cfg_file:str, gui:bool):
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        sys.exit('Environment variable SUMO_HOME not declared.')
    sumo_binary = checkBinary('sumo-gui') if gui else checkBinary('sumo')
    traci.start([sumo_binary, "-c", sumo_cfg_file, '--start' ])
    # traci.start([sumo_binary, "-c", sumo_cfg_file, '--start' , '--no-warnings'])


class Environment_NS_Only:
    '''
    simplest environment: cars are only taking NS route
        - state: always tuple (0)
        - actions: {0,1} -> sets green light for EW, NS respectively
        - reward: +1 for choosing correct action, 0 otherwise
    '''
    
    def __init__(self, sumo_cfg_file:str='intersection/my_net.sumocfg', route_file:str='intersection/my_net.rou.xml', 
                 gui:bool=False, max_steps:int=1000):

        route_car_freq = [0 for _ in range(12)]
        route_car_freq[4] = 0.8
        route_car_freq[10] = 0.8
        self.traffic_generator = TrafficGenerator(route_car_freq=route_car_freq, max_steps=max_steps)
        self.traffic_generator.generate_route_file(route_file=route_file)
        
        sumo_init(sumo_cfg_file, gui)

        self._sumo_cfg_file = sumo_cfg_file
        self._route_file = route_file
        self._gui = gui

    def reset(self):
        """ resets the environment and returns s_0 """
        traci.load(["-c", self._sumo_cfg_file, '--start'])
        return tuple(self._state())

    def step(self, action:int):
        """ 
        takes action in environment
            -> returns s_t+1, r_t, done, info_dict \\
        action : int
            0 : sets EW lights phase
            1 : sets NS lights phase
        """

        if action==0:
            traci.trafficlight.setPhase('0', 0)
        else:  # action==1 or wrong action
            traci.trafficlight.setPhase('0', 2)
        
        traci.simulationStep()

        state = self._state()
        reward = self._reward(action)
        done = self._done()

        return tuple(state), reward, done, {}


    def close(self):
        """ closes the environment """
        traci.close()

    def render(self, type='human'):
        """ renders the current environment state, no need for it though """
        pass

    def _state(self) -> List[int]:
        return [0]

    def _reward(self, action:int) -> int:
        return int(action==1)
    
    def _done(self) -> bool:
        return False


class Environment_Trafic_Lights:
    '''
    traffic lights environment base
        - state: any State inheriting class
        - actions: {0,1} -> sets green light for EW, NS respectively
        - reward: any Reward inheriting class
    
    lookup:
    - PHASE_NS_GREEN   = 0  # action 0 code 00
    - PHASE_NS_YELLOW  = 1
    - PHASE_NSL_GREEN  = 2  # action 1 code 01
    - PHASE_NSL_YELLOW = 3
    - PHASE_EW_GREEN   = 4  # action 2 code 10
    - PHASE_EW_YELLOW  = 5
    - PHASE_EWL_GREEN  = 6  # action 3 code 11
    - PHASE_EWL_YELLOW = 7
    '''

    
    def __init__(self, state_class : State, reward_class  :Union[Reward,DiffReward], 
                 max_steps:int=1000, route_car_freq:Union[None,List[float]]=None,
                 sumo_cfg_file:str='intersection/my_net.sumocfg', route_file:str='intersection/my_net.rou.xml', 
                 gui:bool=False, yellow_duration:int=4, green_duration:int=4):

        self.traffic_generator = TrafficGenerator(route_car_freq=route_car_freq, max_steps=max_steps*(yellow_duration+green_duration))
        self.traffic_generator.generate_route_file(route_file=route_file)
        
        sumo_init(sumo_cfg_file, gui)

        self._sumo_cfg_file = sumo_cfg_file
        self._route_file = route_file
        self._gui = gui
        self._yellow_duration = yellow_duration
        self._green_duration = green_duration

        self._STATE : State = state_class()
        self._REWARD : Reward = reward_class()

        self._last_action = 0

    def reset(self):
        """ resets the environment and returns s_0 """
        self.traffic_generator.generate_route_file(route_file=self._route_file)
        traci.load(["-c", self._sumo_cfg_file, '--start'])
        return tuple(self._state())

    def step(self, action:int):
        """ 
        takes action in environment
            -> returns s_t+1, r_t, done, info_dict \\
        action : int
            0 : sets NS lights green
            1 : sets NS left turn lights green
            2 : sets EW lights green
            3 : sets EW left turn lights green
        """

        if action != self._last_action:
            self._set_yellow_phase(self._last_action)
            self._environment_step(self._yellow_duration)
        
        self._set_green_phase(action)
        self._environment_step(self._green_duration)
        
        self._last_action = action

        state = self._state()
        reward = self._reward()
        done = self._done()

        return tuple(state), reward, done, {}

    def close(self):
        """ closes the environment """
        traci.close()

    def render(self, type='human'):
        """ renders the current environment state, no need for it though """
        pass

    def _state(self) -> List[int]:
        return self._STATE.get()

    def _reward(self) -> int:
        return self._REWARD.calculate()
    
    def _done(self) -> bool:
        return False

    def _set_yellow_phase(self, previous_action:int):
        traci.trafficlight.setPhase("0", previous_action*2 + 1)
    
    def _set_green_phase(self, action:int):
        traci.trafficlight.setPhase("0", action*2)
    
    def _environment_step(self, duration:int):
        """ performs given number of steps in SUMO simulation """
        for _ in range(duration):
            traci.simulationStep()


if __name__=='__main__':
    pass
