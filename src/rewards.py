from abc import abstractmethod
import traci

class DiffReward():
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
    def calculate(self):
        pass 

class WaitDiffReward(DiffReward):
    def read_current(self):
        current = 0
        for lane in self.lanes:
            current += traci.lane.getWaitingTime(lane)

        return current

    def calculate(self):
        return self.stored_val - self.read_current()

    def __str__(self):
        return "Total waiting time decrease"

class QueueDiffReward(DiffReward):
    def read_current(self):
        current = 0
        for lane in self.lanes:
            current += traci.lane.getLastStepHaltingNumber(lane)

        return current

    def calculate(self):
        return self.stored_val - self.read_current()

    def __str__(self):
        return "Total queue decrease"

class CountDiffReward(DiffReward):
    def read_current(self):
        current = 0
        for lane in self.lanes:
            current += traci.lane.getLastStepVehicleNumber(lane)

        return current

    def calculate(self):
        return self.stored_val - self.read_current()

    def __str__(self):
        return "Number of cars decrease (throughput)"

class Reward():
    def __init__(self):
        self.lanes = [lane for lane in traci.lane.getIDList() if 'i' in lane]
        self.type = 'other'

    @abstractmethod
    def calculate(self):
        pass 

class NegWaitReward(Reward):
    def calculate(self):
        current = 0
        for lane in self.lanes:
            current -= traci.lane.getWaitingTime(lane)

        return current 

    def __str__(self):
        return "Negation of total waiting time"

class NegQueueReward(Reward):
    def calculate(self):
        current = 0
        for lane in self.lanes:
            current -= traci.lane.getLastStepHaltingNumber(lane)

        return current 

    def __str__(self):
        return "Negation of total queue"

class SpeedReward(Reward):
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
