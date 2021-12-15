import torch.nn as nn


class DQN_1h(nn.Module):
    def __init__(self, input_size:int=7, hidden_size:int=128, output_size:int=3, **kw):
        super().__init__()
        self.hidden_size = hidden_size
        self.seq = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size)
        )

        self._hp = {
            'name': self.__class__.__name__,
            'input_size': input_size,
            'hidden_sizes': [self.hidden_size],
            'output_size': output_size
        }

    def forward(self, x):
        return self.seq(x)

    def hiperparams(self):
        return self._hp



class DQN_3h(nn.Module):
    def __init__(self, input_size:int=7, hidden_sizes=None, output_size:int=3, **kw):
        super().__init__()

        if hidden_sizes is None or len(hidden_sizes)!=3:
            hidden_sizes = [128,32,8]
        
        self.seq = nn.Sequential(
            nn.Linear(input_size, hidden_sizes[0]),
            nn.ReLU(),
            nn.Linear(hidden_sizes[0], hidden_sizes[1]),
            nn.ReLU(),
            nn.Linear(hidden_sizes[1], hidden_sizes[2]),
            nn.ReLU(),
            nn.Linear(hidden_sizes[2], output_size)
        )

        self._hp = {
            'name': self.__class__.__name__,
            'input_size': input_size,
            'hiden_sizes': hidden_sizes,
            'output_size': output_size
        }

    def forward(self, x):
        return self.seq(x)

    def hiperparams(self):
        return self._hp



if __name__=='__main__':
    dqn3 = DQN_3h()
    print(dqn3.hiperparams())