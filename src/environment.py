import traci
from sumolib import checkBinary

import random

import numpy as np

from . import config

class Environment():
    def __init__(self, state_class, reward_class):
        self.state_class = state_class
        self.reward_class = reward_class

        self.sumo_binary = checkBinary(config.SUMO_BINARY)
        self.state_obj = None
        self.reward_obj = None
        self.phase = -1

    def reset(self):
        self.gen_traffic()
        self.run_sumo()

        self.state_obj = self.state_class()
        self.reward_obj = self.reward_class()

        return self.state_obj.get()

    def step(self, action):
        # TODO: enforce yellow lights and green lights duration (return in info dict?)
        # # chosen phase different from the last phase
        # if self.phase != -1 and action != self.phase:
        #     # set yellow phase 
        #     self.yellow_steps_left = config.YELLOW_DURATION
        # else:
        #     # set green phase
        #     pass

        traci.trafficlight.setPhase('0', action) # junction id as 1st arg
        self.phase = action
        traci.simulationStep()

        new_state = self.state_obj.get()
        reward = self.reward_obj.calculate() 
        done = self.check_done()
        
        return new_state, reward, done, {}

    def check_done(self):
        """
        Check if any car waited for more than MAX_WAITING_TIME.
        """

        done = False

        car_ids = traci.vehicle.getIDList()
        for car_id in car_ids:
            waiting_time = traci.vehicle.getAccumulatedWaitingTime(car_id)
            edge_id = traci.vehicle.getRoadID(car_id)
            if 'i' in edge_id:
                if waiting_time > config.MAX_WAITING_TIME:
                    done = True 
                    break

        return done

    def run_sumo(self):
        traci.start([self.sumo_binary, '-c', './intersection/my_net.sumocfg', 
                    '--start', '-d 100'])

    def gen_traffic(self):
        with open('./intersection/my_net.rou.xml', 'w') as route_file:
            print("""<routes>
            <vType id="car" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" guiShape="passenger"/>
            
            <route id="E_N" edges="1i 2o"/>
            <route id="E_W" edges="1i 3o"/>
            <route id="E_S" edges="1i 4o"/>
            <route id="N_W" edges="2i 3o"/>
            <route id="N_S" edges="2i 4o"/>
            <route id="N_E" edges="2i 1o"/>
            <route id="W_S" edges="3i 4o"/>
            <route id="W_E" edges="3i 1o"/>
            <route id="W_N" edges="3i 2o"/>
            <route id="S_E" edges="4i 1o"/>
            <route id="S_N" edges="4i 2o"/>
            <route id="S_W" edges="4i 3o"/>
            """, file=route_file)

            for step in range(config.MAX_STEPS):
                direction = random.choice(['E_N', 'E_W', 'E_S', 
                                           'N_W', 'N_S', 'N_E',
                                           'W_S', 'W_E', 'W_N',
                                           'S_E', 'S_N', 'S_W'])
                # direction='S_N'
                print(f'    <vehicle id="{direction}_{step}" type="car" route="{direction}" depart="{step}" departLane="random"/>', 
                        file=route_file)
            
            print('</routes>', file=route_file)
