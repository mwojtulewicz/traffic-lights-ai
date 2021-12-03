from abc import abstractmethod
import traci
import numpy as np



class State():
    """ Abstract class for environment's state representation """
    def __init__(self):
        self.lanes = [lane for lane in traci.lane.getIDList() if 'i' in lane]

    @abstractmethod
    def get(self) -> np.ndarray:
        pass 


class SpeedState(State):
    """ Counts mean speed for ever incoming lane """
    # TODO: what about empty lanes?
    def __init__(self):
        super().__init__()
        self.speeds = np.zeros((len(self.lanes),))

    def get(self):
        for i, lane in enumerate(self.lanes):
            self.speeds[i] = traci.lane.getLastStepMeanSpeed(lane)

        return self.speeds

    def __str__(self):
        return "Mean speeds"


class QueueState(State):
    """ Counts how many vehicles are stationary on every incoming lane """
    def __init__(self):
        super().__init__()
        self.queues = np.zeros((len(self.lanes),))

    def get(self):
        for i, lane in enumerate(self.lanes):
            self.queues[i] = traci.lane.getLastStepHaltingNumber(lane)

        return self.queues

    def __str__(self):
        return "Queue lengths"


class CountState(State):
    """ Counts how many vehicles are on every incoming lane """
    def __init__(self):
        super().__init__()
        self.counts = np.zeros((len(self.lanes),))

    def get(self):
        for i, lane in enumerate(self.lanes):
            self.counts[i] = traci.lane.getLastStepVehicleNumber(lane)

        return self.counts

    def __str__(self):
        return "Number of cars"


class WaitState(State):
    """ Cummulative waiting time for each incoming lane """
    def __init__(self):
        super().__init__()
        self.times = np.zeros((len(self.lanes),))

    def get(self):
        for i, lane in enumerate(self.lanes):
            self.times[i] = traci.lane.getWaitingTime(lane)

        return self.times

    def __str__(self):
        return "Total waiting times"
