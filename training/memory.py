import numpy as np
import collections
import torch
from typing import Tuple, List, Union


# experience tuple type: (state_t, action_t, reward_t, state_t+1, done)
ExpTuple = Tuple[ List[int], int, Union[int,float], List[int], bool ]


class ReplayBuffer:
    
    def __init__(self, max_length:int, device:Union[None, str]=None):
        self._max_length = max_length
        
        self._memory = collections.deque(maxlen=max_length)
        self._tail_offset = 0
        self._full = False

        if device is not None:
            self._torch = True
            self._device = device
            print(f'RB torch, device: {self._device}')
        else:
            self._torch = False

    def append(self, experience_tuple:ExpTuple):
        if self._full:
            self._memory[self._tail_offset] = experience_tuple
            self._tail_offset += 1
            if self._tail_offset == self._max_length:
                self._tail_offset = 0
        else:
            self._memory.append(experience_tuple)
            self._tail_offset += 1
            if self._tail_offset == self._max_length:
                self._full = True
                self._tail_offset = 0

    def sample(self, size:int) -> Tuple[np.ndarray]:
        size = min(size, len(self))
        indicies = np.random.choice(len(self), size=size)
        samples = [self._memory[idx] for idx in indicies]
        return self._vectorize(samples)
    
    def _vectorize(self, samples:List[ExpTuple]) -> Tuple[np.ndarray]:
        states, actions, rewards, next_states, dones = [], [], [], [], []
        for sample in samples:
            states.append(sample[0])
            actions.append(sample[1])
            rewards.append(sample[2])
            next_states.append(sample[3])
            dones.append(sample[4])
        if not self._torch:
            return np.array(states), np.array(actions), np.array(rewards), np.array(next_states), np.array(dones)
        else:
            states = torch.FloatTensor(np.array(states, copy=False, dtype=np.float64)).to(self._device)
            actions = torch.LongTensor(np.array(actions, copy=False, dtype=np.int64)).to(self._device)
            rewards = torch.FloatTensor(np.array(rewards, copy=False, dtype=np.float64)).to(self._device)
            next_states = torch.FloatTensor(np.array(next_states, copy=False, dtype=np.float64)).to(self._device)
            dones = torch.BoolTensor(np.array(dones, copy=False, dtype=bool)).to(self._device)
            return states, actions, rewards, next_states, dones

    def __getitem__(self, idx:int) -> ExpTuple:
        return self._memory[idx]

    def __len__(self) -> int:
        if self._full:
            return self._max_length
        else:
            return self._tail_offset


class MemoryPalace:
    # TODO: implement :)
    pass



if __name__=='__main__':

    rb = ReplayBuffer(4)
    
    for i in range(9):
        et = ([i],i,i,i,True)
        rb.append(et)
        print(rb._tail_offset, rb._memory, len(rb), rb[i%4])