# general
GUI = True
TRAIN_MODE = False

# loop
NUM_EPISODES = 125 if TRAIN_MODE else 1 # TODO: change
MAX_STEPS = 2000 # TODO: change
GAMMA = 0.9 # TODO: change
READ_EVERY = 4 # number of simulation steps on 1 agent step

# environment
YELLOW_DURATION = 2 # TODO: change
MAX_WAITING_TIME = 90 # TODO: change
NUM_ACTIONS = 4
STATES_LEN = 16

# training
MEMORY_SIZE = 8192 # TODO: change
NUM_TRAIN_STEPS = 128 # TODO: change
BATCH_SIZE = 32 # TODO: change