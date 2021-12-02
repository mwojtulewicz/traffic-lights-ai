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

    edges = ('1i', '2i', '3i', '4i')

    # pętla po epizodach
    for i in range(1000):
        traci.gui.screenshot(traci.gui.getIDList()[0], f'./screenshots/{i}.png')
        traci.simulationStep()
        # print(traci.edge.getLastStepHaltingNumber('1i'))
        
        for edge in edges:
            print(f'{edge}: {traci.edge.getLastStepHaltingNumber(edge)}')