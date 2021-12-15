import numpy as np
import itertools
from typing import List, Union, Tuple


class TrafficGenerator:
    def __init__(self, max_steps:int, route_car_freq:Union[None, List[float]] = None):
        self.max_steps = max_steps
        # nodes
        self.nodes = {1:'E', 2:'N', 3:'W', 4:'S'}
        # all possbile routes - (id, spawn_edge, dest_edge)
        self.routes = [self.create_route_tuple(start_id, turn) for start_id in self.nodes.keys() for turn in 'rsl']

        if route_car_freq is None:
            self.route_car_freq = [.2 for _ in self.routes]
        else:
            self.route_car_freq = route_car_freq

    def generate_route_file(self, seed:Union[None, int] = None, route_file:str = 'intersection/my_net.rou.xml'):
        if seed is not None:
            np.random.seed(seed)
        
        with open(route_file, 'w') as rf:
            print('<routes> \n<vType accel="1.0" decel="4.5" id="standard_car" length="5.0" minGap="2.5" maxSpeed="25" sigma="0.5" />', file=rf)
            
            for route_id, spawn_edge, dest_edge in self.routes:
                print(f'<route id="{route_id}" edges="{spawn_edge} {dest_edge}"/>', file=rf)

            for i in range(self.max_steps):
                rnds = np.random.random(size=len(self.routes))
                for j,(rnd,(route,_,_)) in enumerate(zip(rnds, self.routes)):
                    if rnd<=self.route_car_freq[j]:
                        print(f'<vehicle id="{route}_{i}" type="standard_car" route="{route}" depart="{i}" departLane="random" departSpeed="10" />', file=rf)

            print('</routes>', file=rf)
    
    def create_route_tuple(self, start_id:int, turn:str) -> Tuple[str, str, str]:
        # returns a tuple: route_name, start_edge, destination_edge
        node_lut = [0, 1, 2, 3, 4, 1, 2, 3]
        turn_lut = {'r':1, 's':2, 'l':3}
        
        start_name = self.nodes[start_id]
        dest_id = node_lut[start_id + turn_lut.get(turn, 0)]
        dest_name = self.nodes[dest_id]
        
        _name = f'{start_name}_{dest_name}'
        _s_edge = f'{start_id}i'
        _d_edge = f'{dest_id}o'

        return _name, _s_edge, _d_edge



if __name__=='__main__':
    gen = TrafficGenerator(10)
    print(gen.nodes, gen.routes, sep='\n')
    gen.generate_route_file(seed=0)
