import math
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.agents.base_agent import  SimpleControllerState
from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3 as vector3, Rotator

from objects import *
from states import *
from states2 import *

'''

if self.opponents[0].location[2]>200 or abs(self.ball.location[1])> 5100:
            car = CarState(boost_amount=100, physics=Physics(velocity=vector3(0,0,0),angular_velocity=vector3(0,0,0),location=vector3(0,0,20),rotation=Rotator(0,-1,0)))
            ball = BallState(physics=Physics(location=vector3(0,3000,94),angular_velocity=vector3(0,0,0), velocity=vector3(10,0,0)))
            game = GameState(ball=ball, cars = {self.index: car})
            self.set_game_state(game)
'''

class watchout(BaseAgent):
    def initialize_agent(self):
        self.me = carObject(self.index)
        self.ball = ballObject()
        self.teammates = []
        self.opponents = []
        
        self.states = [vector_shot_test()]
        self.state = self.states[0]
        self.c = SimpleControllerState()

        self.time = 0.0
        self.sinceJump = 0.0
        #need to get boostpad info

    def test(self):
        car = CarState(boost_amount=100, physics=Physics(velocity=vector3(0,0,0),angular_velocity=vector3(0,0,0),location=vector3(3000,3000,20),rotation=Rotator(0,1.5,0)))
        ball = BallState(physics=Physics(location=vector3(0,-side(self.team)*3000,94),angular_velocity=vector3(0,0,0), velocity=vector3(0,0,3000)))
        game = GameState(ball=ball, cars = {self.index: car})
        self.set_game_state(game)
        self.state = vector_shot_test()
        
    
    def refresh(self):
        self.c.__init__() #don't hurt me pls
        return self.c
        
    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.process(packet)
        self.refresh()
        if self.opponents[0].location[2]>200:# or abs(self.ball.location[1])> 5100:
            self.test()
        controller = self.state.execute(self)
        #print(controller.jump)
        return controller

    def process(self,packet):
        elapsed = packet.game_info.seconds_elapsed-self.time
        self.sinceJump += elapsed
        self.time = packet.game_info.seconds_elapsed
        self.ball.update(packet.game_ball)
        for i in range(packet.num_cars):
            car = packet.game_cars[i]
            if i == self.index:
                self.me.update(car)
            elif car.team == self.team:
                flag = True
                for teammate in self.teammates:
                    if i == teammate.index:
                        teammate.update(car)
                        flag = False
                if flag:
                    self.teammates.append(carObject(i,car))
            else:
                flag = True
                for opponent in self.opponents:
                    if i == opponent.index:
                        opponent.update(car)
                        flag = False
                if flag:
                    self.opponents.append(carObject(i,car))
