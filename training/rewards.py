from abc import abstractmethod
import traci



class DiffReward():
    """ Abstract class for environment's reward which is calculated as difference between two steps """
    def __init__(self):
        self.lanes = [lane for lane in traci.lane.getIDList() if 'i' in lane]
        self.type = 'diff'
        self.stored_val = None

    @abstractmethod
    def read_current(self):
        pass 

    def save_current(self):
        self.stored_val = self.read_current()

    @abstractmethod
    def calculate(self) -> float:
        pass 

class WaitDiffReward(DiffReward):
    """ Difference in sum of vehicles' waiting times """
    def read_current(self):
        current = 0
        for lane in self.lanes:
            current += traci.lane.getWaitingTime(lane)

        return current

    def calculate(self):
        prev_value = self.stored_val
        self.save_current()
        return -(self.stored_val - prev_value)

    def __str__(self):
        return "Total waiting time decrease"

class QueueDiffReward(DiffReward):
    """ Difference in number of waiting vehicles on incoming lanes """
    def read_current(self):
        current = 0
        for lane in self.lanes:
            current += traci.lane.getLastStepHaltingNumber(lane)

        return current

    def calculate(self):
        prev_value = self.stored_val
        self.save_current()
        return -(self.stored_val - prev_value)

    def __str__(self):
        return "Total queue decrease"

class CountDiffReward(DiffReward):
    """ Difference in number of vehicles on incoming lanes"""
    def read_current(self):
        current = 0
        for lane in self.lanes:
            current += traci.lane.getLastStepVehicleNumber(lane)

        return current

    def calculate(self):
        prev_value = self.stored_val
        self.save_current()
        return -(self.stored_val - prev_value)

    def __str__(self):
        return "Number of cars decrease (throughput)"

class Reward():
    """ Abstract class for environment's reward which is calculated every step """
    def __init__(self):
        self.lanes = [lane for lane in traci.lane.getIDList() if 'i' in lane]
        self.type = 'other'

    @abstractmethod
    def calculate(self):
        pass 

class NegWaitReward(Reward):
    """ Negative sum of vehicles' waiting times """
    def calculate(self):
        current = 0
        for lane in self.lanes:
            current -= traci.lane.getWaitingTime(lane)

        return current 

    def __str__(self):
        return "Negation of total waiting time"

class NegQueueReward(Reward):
    """ Negative number of waiting cars on incoming lanes """
    def calculate(self):
        current = 0
        for lane in self.lanes:
            current -= traci.lane.getLastStepHaltingNumber(lane)

        return current 

    def __str__(self):
        return "Negation of total queue"

class SpeedReward(Reward):
    """ Sum of lanes' mean speeds """
    def __init__(self):
        super().__init__()
        self.lanes = traci.lane.getIDList()

    def calculate(self):
        current = 0
        for lane in self.lanes:
            current += traci.lane.getLastStepMeanSpeed(lane)

        return current 

    def __str__(self):
        return "Sum of speeds"
