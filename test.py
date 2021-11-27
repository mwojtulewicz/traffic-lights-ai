import os
import sys

import traci
from sumolib import checkBinary

if __name__ == '__main__':
    os.environ['SUMO_HOME'] = '/usr/share/sumo/'

    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)

    sumo_binary = checkBinary('sumo-gui')
    traci.start([sumo_binary, '-c', './intersection/my_net.sumocfg', '--start', '-d 100'])

    # pętla po epizodach
    for i in range(1000):
        traci.simulationStep()
        # print(traci.edge.getLastStepHaltingNumber('1i'))
        
        if i < 500:
            traci.trafficlight.setPhase('0', 0)
        else:
            traci.trafficlight.setPhase('0', 2)