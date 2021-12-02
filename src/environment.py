import traci
from sumolib import checkBinary

import random

import numpy as np

from . import config

class Environment():
    def __init__(self, sumo_binary):
        self.sumo_binary = checkBinary(sumo_binary)

        self.edges = ('1i', '2i', '3i', '4i') # TODO: change to lanes
        self.phase = -1 # TODO
        self.yellow_steps_left = 0
        self.waiting_time = 0
        self.max_steps = config.MAX_STEPS

    def reset(self):
        # nadpisanie odpowiednich zmiennych
        self.gen_traffic()
        self.run_sumo()

        return self.get_state()

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
        current_state = self.get_state()

        current_waiting_time, done = self.get_waiting_time()
        reward = self.waiting_time - current_waiting_time
        self.waiting_time = current_waiting_time
        
        return current_state, reward, done, {}

    def get_state(self):
        """
        State is represented by 4-element vector,
        where each element is a total number of halting vehicles
        on a given edge.
        """

        state = np.zeros(len(self.edges))
        for i, edge in enumerate(self.edges):
            state[i] = traci.edge.getLastStepHaltingNumber(edge)

        return state

    def get_waiting_time(self):
        """
        Use sum of waiting times to determine reward.
        """

        total_waiting_time = 0
        done = False

        car_ids = traci.vehicle.getIDList()
        for car_id in car_ids:
            waiting_time = traci.vehicle.getAccumulatedWaitingTime(car_id)
            edge_id = traci.vehicle.getRoadID(car_id)
            if 'i' in edge_id:
                if waiting_time > config.MAX_WAITING_TIME:
                    done = True 
                    break

                total_waiting_time += waiting_time

        return total_waiting_time, done

    def run_sumo(self):
        traci.start([self.sumo_binary, '-c', './intersection/my_net.sumocfg', 
                    '--start', '-d 100'])

    def gen_traffic(self):
        with open('./intersection/my_net.rou.xml', 'w') as route_file:
            print("""<routes>
            <vType id="car" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" guiShape="passenger"/>
            
            <route id="right" edges="3i 1o" />
            <route id="left" edges="1i 3o" />
            <route id="down" edges="2i 4o" />
            <route id="up" edges="4i 2o" />
            """, file=route_file)

            for step in range(self.max_steps):
                # direction = random.choice(['up', 'right', 'down', 'left'])
                direction = 'up'
                print(f'    <vehicle id="{direction}_{step}" type="car" route="{direction}" depart="{step}" />', 
                        file=route_file)
            
            print('</routes>', file=route_file)
