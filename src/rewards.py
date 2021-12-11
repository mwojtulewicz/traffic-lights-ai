from abc import abstractmethod
import traci

def get_rewards_tuple():
    return (WaitDiffReward, QueueDiffReward, 
            NegWaitReward, NegQueueReward, ThroughputReward)

class DiffReward():
    def __init__(self):
        self.lanes = [lane for lane in traci.lane.getIDList() if 'i' in lane]
        # self.type = 'diff'
        self.stored_val = 0

    @abstractmethod
    def read_current(self):
        pass 

    # @abstractmethod
    def calculate(self):
        prev_val = self.stored_val
        self.stored_val = self.read_current()
        return prev_val - self.stored_val 

class FuelDiffReward(DiffReward):
    def read_current(self):
        current = 0
        for lane in self.lanes:
            current += traci.lane.getFuelConsumption(lane)

        return current

    @staticmethod
    def desc():
        return "Total fuel consumption difference"

class WaitDiffReward(DiffReward):
    def read_current(self):
        current = 0
        for lane in self.lanes:
            current += traci.lane.getWaitingTime(lane)

        return current

    @staticmethod
    def desc():
        return "Total waiting time difference"

class QueueDiffReward(DiffReward):
    def read_current(self):
        current = 0
        for lane in self.lanes:
            current += traci.lane.getLastStepHaltingNumber(lane)

        return current

    @staticmethod
    def desc():
        return "Total queue difference"

# class CountDiffReward(DiffReward):
#     def read_current(self):
#         current = 0
#         for lane in self.lanes:
#             current += traci.lane.getLastStepVehicleNumber(lane)

#         return current

#     def __str__(self):
#         return "Total number of cars difference"

# class SpeedDiffReward(DiffReward):
#     def read_current(self):
#         current = 0
#         for lane in self.lanes:
#             current += traci.lane.getLastStepVehicleNumber(lane)

#         return current

#     def calculate(self):
#         prev_val = self.stored_val
#         self.save_current()
#         return prev_val - self.stored_val

#     def __str__(self):
#         return "Total number of cars difference"

class Reward():
    def __init__(self):
        self.lanes = [lane for lane in traci.lane.getIDList() if 'i' in lane]
        # self.type = 'other'

    @abstractmethod
    def calculate(self):
        pass 

class NegFuelReward(Reward):
    def calculate(self):
        current = 0
        for lane in self.lanes:
            current -= traci.lane.getFuelConsumption(lane)

        return current 

    @staticmethod
    def desc():
        return "Negation of total fuel consumption"

class NegWaitReward(Reward):
    def calculate(self):
        current = 0
        for lane in self.lanes:
            current -= traci.lane.getWaitingTime(lane)

        return current 

    @staticmethod
    def desc():
        return "Negation of total waiting time"

class NegQueueReward(Reward):
    def calculate(self):
        current = 0
        for lane in self.lanes:
            current -= traci.lane.getLastStepHaltingNumber(lane)

        return current 

    @staticmethod
    def desc():
        return "Negation of total queue"

# class SpeedReward(Reward):
#     def __init__(self):
#         super().__init__()
#         self.lanes = traci.lane.getIDList()

#     def calculate(self):
#         current = 0
#         for lane in self.lanes:
#             current += traci.lane.getLastStepMeanSpeed(lane)

#         return current 

#     def __str__(self):
#         return "Sum of speeds"

class ThroughputReward():
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

    