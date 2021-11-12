#!/usr/bin/env python
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2009-2021 German Aerospace Center (DLR) and others.
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# https://www.eclipse.org/legal/epl-2.0/
# This Source Code may also be made available under the following Secondary
# Licenses when the conditions for such availability set forth in the Eclipse
# Public License 2.0 are satisfied: GNU General Public License, version 2
# or later which is available at
# https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
# SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-or-later

# @file    runner.py
# @author  Lena Kalleske
# @author  Daniel Krajzewicz
# @author  Michael Behrisch
# @author  Jakob Erdmann
# @date    2009-03-26

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa


def generate_routefile():
    random.seed(42)  # make tests reproducible
    N = 3600  # number of time steps
    # demand per second from different directions
    pWE = 1. / 3
    pEW = 1. / 3
    pNS = 1. / 1.5
    pSN = 1. / 2.5
    with open("my_net.rou.xml", "w") as routes:
        print("""<routes>
        <vType id="car" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" guiShape="passenger"/>

        <route id="right" edges="3i 1o" />
        <route id="left" edges="1i 3o" />
        <route id="down" edges="2i 4o" />
        <route id="up" edges="4i 2o" />""", file=routes)
        vehNr = 0
        for i in range(N):
            if random.uniform(0, 1) < pWE:
                print(f'    <vehicle id="right_{vehNr}" type="car" route="right" depart="{i}" />', file=routes)
                vehNr += 1
            if random.uniform(0, 1) < pEW:
                print(f'    <vehicle id="left_{vehNr}" type="car" route="left" depart="{i}" />', file=routes)
                vehNr += 1
            if random.uniform(0, 1) < pNS:
                print(f'    <vehicle id="down_{vehNr}" type="car" route="down" depart="{i}" />', file=routes)
                vehNr += 1
            if random.uniform(0, 1) < pSN:
                print(f'    <vehicle id="up_{vehNr}" type="car" route="up" depart="{i}" />', file=routes)
                vehNr += 1
        print("</routes>", file=routes)

# The program looks like this
#    <tlLogic id="0" type="static" programID="0" offset="0">
# the locations of the tls are      NESW
#        <phase duration="31" state="GrGr"/>
#        <phase duration="6"  state="yryr"/>
#        <phase duration="31" state="rGrG"/>
#        <phase duration="6"  state="ryry"/>
#    </tlLogic>


def run():
    """execute the TraCI control loop"""
    step = 0
    # we start with phase 2 where EW has green
    # traci.trafficlight.setPhase("0", 2)
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        # if traci.trafficlight.getPhase("0") == 2:
        #     # we are not already switching
        #     if traci.inductionloop.getLastStepVehicleNumber("0") > 0:
        #         # there is a vehicle from the north, switch
        #         traci.trafficlight.setPhase("0", 3)
        #     else:
        #         # otherwise try to keep green for EW
        #         traci.trafficlight.setPhase("0", 2)
        step += 1
    traci.close()
    sys.stdout.flush()


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # first, generate the route file for this simulation
    generate_routefile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "my_net.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()
