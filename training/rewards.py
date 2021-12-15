from abc import abstractmethod
import traci


def get_rewards_tuple(who: str = ""):
    """ Returns rewards tuple for experiments based on ```who``` is asking ;) """
    if who == "Wojtek":
        return (WaitDiffReward, QueueDiffReward)
    elif who == "Mateusz":
        return (NegWaitReward, NegQueueReward, ThroughputReward)
    else:
        raise Exception("Who are you?")
    
def get_metrics_tuple():
    """ Returns a tuple containing all possible metrics for testing """
    return QueueMetric, ThroughputReward


class DiffReward():
    """ Abstract class for environment's reward which is calculated as difference between two steps """
    def __init__(self):
        self.lanes = [lane for lane in traci.lane.getIDList() if 'i' in lane]
        self.type = 'diff'
        self.stored_val = 0

    @abstractmethod
    def read_current(self):
        pass 

    def save_current(self):
        self.stored_val = self.read_current()

    def calculate(self) -> float:
        prev_val = self.stored_val
        self.stored_val = self.read_current()
        return prev_val - self.stored_val


class WaitDiffReward(DiffReward):
    """ Difference in sum of vehicles' waiting times """
    def read_current(self):
        current = 0
        for lane in self.lanes:
            current += traci.lane.getWaitingTime(lane)

        return current

    def __str__(self):
        return "Total waiting time decrease"
    
    @staticmethod
    def desc():
        return "Total waiting time difference"


class QueueDiffReward(DiffReward):
    """ Difference in number of waiting vehicles on incoming lanes """
    def read_current(self):
        current = 0
        for lane in self.lanes:
            current += traci.lane.getLastStepHaltingNumber(lane)

        return current

    def __str__(self):
        return "Total queue decrease"
    
    @staticmethod
    def desc():
        return "Total queue difference"


class CountDiffReward(DiffReward):
    """ Difference in number of vehicles on incoming lanes"""
    def read_current(self):
        current = 0
        for lane in self.lanes:
            current += traci.lane.getLastStepVehicleNumber(lane)

        return current

    def __str__(self):
        return "Number of cars decrease (throughput)"
    
    @staticmethod
    def desc():
        return "Number of cars decrease (throughput)"


class Reward():
    """ Abstract class for environment's reward which is calculated every step """
    def __init__(self):
        self.lanes = [lane for lane in traci.lane.getIDList() if 'i' in lane]
        self.type = 'other'

    @abstractmethod
    def calculate(self) -> float:
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
    
    @staticmethod
    def desc():
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
    
    @staticmethod
    def desc():
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
    
    @staticmethod
    def desc():
        return "Sum of speeds"


class ThroughputReward():
    """ Number of vehicles that passed the intersection since last step """
    def __init__(self):
        self.vehicles = self.read_current() 

    def read_current(self):
        vehicles = traci.vehicle.getIDList()
        return [vehicle for vehicle in vehicles if
                                    'i' in traci.vehicle.getRoadID(vehicle)]

    def calculate(self):
        old_vehicles = self.vehicles # incoming vehicles at t_0
        self.vehicles = self.read_current() # incoming vehicles at t_1

        current = 0
        for vehicle in old_vehicles:
            if vehicle not in self.vehicles: # vehicle left incoming lane
                current += 1

        return current 

    @staticmethod
    def desc():
        return "Total throughput"


class QueueMetric(Reward):
    """ Number of waiting cars on incoming lanes - metric"""
    
    def calculate(self):
        current = 0
        for lane in self.lanes:
            current += traci.lane.getLastStepHaltingNumber(lane)

        return current 

    def __str__(self):
        return "Total queue metric"
    
    @staticmethod
    def desc():
        return "Total queue metric"
