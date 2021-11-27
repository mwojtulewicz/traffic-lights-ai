import random

import numpy as np

from .memory import Memory
from .nn import get_model
from . import config

class Agent():
    def __init__(self):
        self.nn = get_model() # TODO: string-klucz wybierający różne modele
        self.memory = Memory(config.MEMORY_SIZE) # TODO: zmienić size
        self.num_actions = config.NUM_ACTIONS 
        self.num_train_steps = config.NUM_TRAIN_STEPS

    def act(self, state, epsilon):
        if random.random() < epsilon:
            return random.randint(0, self.num_actions - 1)
        else:
            return np.argmax(self.nn.predict(np.expand_dims(state), 0))

    def train(self, states, q_sa):
        for _ in range(config.NUM_TRAIN_STEPS):
            batch = self.memory.get_samples(config.BATCH_SIZE)

            states = np.array([sample[0] for sample in batch])
            next_states = np.array([sample[-1] for sample in batch])

            actions_pred = self.nn.predict(states)
            next_actions_pred = self.nn.predict(next_states)

            self.nn.fit(states, , epochs=1, verbose=0)

    def save_model(self):
        pass

    