import random

class Memory():
    """
    Handles experience replay.
    Replay memory implemented as list-queue.
    """

    def __init__(self, size):
        self.samples = [] # using list due to no random sampling using Queue
        self.size = size 

    def add_sample(self, sample):
        self.samples.append(sample)
        if len(self.samples) > self.size:
            self.samples.pop(0)

    def get_samples(self, n):
        if len(self.samples) < n:
            return self.samples 
        else:
            return random.sample(self.samples, n)
    