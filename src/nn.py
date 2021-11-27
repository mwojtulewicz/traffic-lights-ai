from tensorflow.keras.layers import Input, Dense
from tensorflow.keras import Model
from tensorflow.keras import losses
from tensorflow.keras.optimizers import Adam

def get_model():
    inputs = Input(shape=(4,)) # TODO: zmienić

    x = Dense(64, activation='relu')(inputs)
    for _ in range(5):
        x = Dense(64, activation='relu')(x)

    outputs = Dense(4, activation='linear')(x)

    model = Model(inputs=inputs, outputs=outputs)
    model.compile(loss='mse', optimizer='adam')

    return model