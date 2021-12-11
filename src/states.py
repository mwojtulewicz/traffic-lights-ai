from abc import abstractmethod
import traci
import numpy as np

def get_states_tuple():
    return (QueueState, CountState, WaitState)

class State():
    def __init__(self):
        self.lanes = [lane for lane in traci.lane.getIDList() if 'i' in lane]
        self.shape = (len(self.lanes),)

    @abstractmethod
    def get(self):
        pass 

# class SpeedState(State):
#     # TODO: what about empty lanes?
#     def __init__(self):
#         super().__init__()
#         self.speeds = np.zeros((len(self.lanes),))

#     def get(self):
#         for i, lane in enumerate(self.lanes):
#             self.speeds[i] = traci.lane.getLastStepMeanSpeed(lane)

#         return self.speeds

#     def __str__(self):
#         return "Mean speed (per lane)"

class QueueState(State):
    def __init__(self):
        super().__init__()
        self.queues = np.zeros((len(self.lanes),))

    def get(self):
        for i, lane in enumerate(self.lanes):
            self.queues[i] = traci.lane.getLastStepHaltingNumber(lane)

        return self.queues

    @staticmethod
    def desc():
        return "Queue length (per lane)"

class CountState(State):
    def __init__(self):
        super().__init__()
        self.counts = np.zeros((len(self.lanes),))

    def get(self):
        for i, lane in enumerate(self.lanes):
            self.counts[i] = traci.lane.getLastStepVehicleNumber(lane)

        return self.counts

    @staticmethod
    def desc():
        return "Number of cars (per lane)"

class WaitState(State):

    def __init__(self):
        super().__init__()
        self.times = np.zeros((len(self.lanes),))

    def get(self):
        for i, lane in enumerate(self.lanes):
            self.times[i] = traci.lane.getWaitingTime(lane)

        return self.times

    @staticmethod
    def desc():
        return "Sum of waiting time (per lane)"

class FuelState(State):
    def __init__(self):
        super().__init__()
        self.fuels = np.zeros((len(self.lanes),))

    def get(self):
        for i, lane in enumerate(self.lanes):
            self.fuels[i] = traci.lane.getFuelConsumption(lane)

        return self.fuels

    @staticmethod
    def desc():
        return "Sum of fuel consumption (per lane)"