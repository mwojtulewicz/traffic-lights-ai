from tensorflow.keras.layers import Input, Dense
from tensorflow.keras import Model
from tensorflow.keras import losses
from tensorflow.keras.optimizers import Adam

from . import config

def get_model(input_shape):
    inputs = Input(shape=input_shape)

    x = Dense(64, activation='relu')(inputs)
    for _ in range(5):
        x = Dense(64, activation='relu')(x)

    outputs = Dense(config.NUM_ACTIONS, activation='linear')(x)

    model = Model(inputs=inputs, outputs=outputs)
    model.compile(loss='mse', optimizer='adam')

    return model