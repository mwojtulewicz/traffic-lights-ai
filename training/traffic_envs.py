import numpy as np
import traci
import sys, os
from sumolib import checkBinary
from generator import TrafficGenerator
from typing import List, Union, Tuple

def sumo_init(sumo_cfg_file:str, gui:bool):
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        sys.exit('Environment variable SUMO_HOME not declared.')
    sumo_binary = checkBinary('sumo-gui') if gui else checkBinary('sumo')
    traci.start([sumo_binary, "-c", sumo_cfg_file, '--start' , '--no-warnings'])


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


if __name__=='__main__':
    pass
