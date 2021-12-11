# general
GUI = False
TRAIN_MODE = True

# loop
NUM_EPISODES = 10 if TRAIN_MODE else 1 # TODO: change
MAX_STEPS = 1000 # TODO: change
GAMMA = 0.9 # TODO: change
READ_EVERY = 4 # number of simulation steps on 1 agent step

# environment
YELLOW_DURATION = 2 # TODO: change
MAX_WAITING_TIME = 90 # TODO: change
NUM_ACTIONS = 4
STATES_LEN = 16

# training
MEMORY_SIZE = 640 # TODO: change
NUM_TRAIN_STEPS = 20 # TODO: change
BATCH_SIZE = 32 # TODO: change