import math
import pickle
from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3 as vector3, Rotator

def read(file):
    with open(file, 'rb') as f:
        return pickle.load(f)
def write(data,file):
    with open(file, 'wb') as f:
        pickle.dump(data,f)


class scenario:
    def __init__(self,car,ball,teammates,opponents):
        self.car = car
        self.ball = ball
        self.teammates = teammates
        self.opponents = opponents
        self.results = []

class test:
    def __init__(self,scenarios,,end_conditions,markers):
        self.scenarios = scenarios
        self.end_conditions = end_conditions
        self.markers = markers

        self.active = self.scenarios[]
            
