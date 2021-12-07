import random

import numpy as np

from .memory import Memory
from .nn import get_model
from . import config

class Agent():
    def __init__(self):
        self.memory = Memory(config.MEMORY_SIZE) # TODO: zmienić size
        self.num_actions = config.NUM_ACTIONS 
        self.states_len = config.STATES_LEN
        self.nn = get_model()

        if not config.TRAIN_MODE:
            self.load_model()

    def act(self, state, epsilon):
        if random.random() < epsilon and config.TRAIN_MODE:
            return random.randint(0, self.num_actions - 1)
        else:
            return np.argmax(self.nn.predict(np.expand_dims(state, 0)))

    def train(self):
        for _ in range(config.NUM_TRAIN_STEPS):
            batch = self.memory.get_samples(config.BATCH_SIZE)

            states = np.array([sample[0] for sample in batch])
            next_states = np.array([sample[-1] for sample in batch])

            q_pred = self.nn.predict(states)
            next_q_pred = self.nn.predict(next_states)

            # calculating "true" labels
            x = np.zeros((config.BATCH_SIZE, self.states_len))
            y = np.zeros((config.BATCH_SIZE, self.num_actions))

            for i, sample in enumerate(batch):
                old_state, action, reward, _ = sample
                x[i] = old_state
                q_pred[i][action] = reward + config.GAMMA * np.amax(next_q_pred[i])
                y[i] = q_pred[i]

            self.nn.fit(x, y, epochs=1, verbose=1)

    def save_model(self):
        self.nn.save_weights('./checkpoints/checkpoint.h5')

    def load_model(self):
        self.nn.load_weights('./checkpoints/checkpoint.h5')

    