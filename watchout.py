import math
import time
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.agents.base_agent import  SimpleControllerState
from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3 as vector3, Rotator

from objects import *
from routines import *
from graphics import *
from strategy import *

class watchout(BaseAgent):
    def initialize_agent(self):
        self.c = SimpleControllerState()
        self.me = carObject(self.index)
        self.ball = ballObject()
        
        field_info = self.get_field_info()

        self.all_boosts = []
        self.small_boosts = []
        self.large_boosts = []
        for i in range(field_info.num_boosts):
            boost = field_info.boost_pads[i]
            temp = boostObject(i,boost.location,boost.is_full_boost)
            self.all_boosts.append(temp)
            if boost.is_full_boost:
                self.large_boosts.append(temp)
            else:
                self.small_boosts.append(temp)
 
        self.friends = []
        self.foes = []
        self.friend_goal = goalObject(self.team)
        self.foe_goal = goalObject(not self.team)
        
        self.stack = []
        self.time = 0.0
        self.need_setup = True
        self.kickoff = False
        self.made_kickoff_routine = False

        self.gui = gui(self,True) #True to enable GUI

    def watchdog(self):
        """
        Kickoff
        """
        if self.kickoff == True and self.made_kickoff_routine == False:
            self.stack.append(kickoff())
            self.made_kickoff_routine = True
        elif self.kickoff == False and self.made_kickoff_routine == True:
            self.made_kickoff_routine = False
        """
        1v1 Strategy
        """
        if len(self.stack) < 1:
            if shotConeRatio(self.me,self.ball.location, self.foe_goal.left_post, self.foe_goal.right_post) < -0.0:
                shots = shotFinder(self,self.foe_goal.left_post, self.foe_goal.right_post)
                if len(shots) > 0:
                    best = 0
                    for i in range(len(shots)):
                        if shots[i].ratio < shots[best].ratio:
                            best = i
                    medium = best // 2
                    self.stack.append(shot(shots[medium]))
                else:
                    pass
        """
                    left = Vector3(-3600*side(self.team),-5000*self.team,0)
                    right = Vector3(3600*side(self.team),-5000*self.team,0)
                    shots = shotFinder(self, left, right)
                    if len(shots) > 0:
                        best = 0
                        for i in range(len(shots)):
                            if shots[i].ratio < shots[best].ratio:
                                best = i
                        medium = best // 4
                        self.stack.append(shot(shots[medium]))
                    elif self.me.boost < 50:
                        my_dist = (self.friend_goal.location-self.me.location).magnitude()
                        temps = [boost for boost in self.large_boosts if (self.friend_goal.location-boost.location).magnitude()<my_dist and boost.active]
                        if len(temps) > 0:
                            closest = temps[0]
                            for boost in temps:
                                if (boost.location - self.me.location).magnitude() < (closest.location - self.me.location).magnitude():
                                    closest = boost
                            self.stack.append(simpleBoost(closest))
                    else:
                        self.stack.append(simpleBoost(closest))
            else:
                left = Vector3(-900*side(self.team),4100*side(self.team),0)
                right = Vector3(-900*side(self.team),-4100*side(self.team),0)
                self.gui.line(self.me.location, left, (255,255,0,255))
                self.gui.line(self.me.location, right, (255,0,0,255))
                ratio = shotConeRatio(self.me,self.ball.location,right,left)
                if  ratio< 0.0:
                    shots = shotFinder(self, right, left)
                else:
                    left = Vector3(900*side(self.team),4100*side(self.team),0)
                    right = Vector3(900*side(self.team),-4100*side(self.team),0)
                    shots = shotFinder(self, left, right)
                if len(shots) > 0:
                    best = 0
                    for i in range(len(shots)):
                        if shots[i].ratio < shots[best].ratio:
                            best = i
                    medium = best // 4
                    self.stack.append(shot(shots[medium]))
                else:
                    print("idk how you got here_ 2")
            """
            

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.preprocess(packet)
        self.c.__init__()
        self.watchdog()
        if len(self.stack) > 0:
            self.stack[-1].run(self)
        self.gui.update(self)
        return self.c

    def preprocess(self,packet):
        self.time = packet.game_info.seconds_elapsed
        
        self.ball.update(packet.game_ball)
        self.me.update(packet.game_cars)

        for friend in self.friends: friend.update(packet.game_cars)
        for foe in self.foes: foe.update(packet.game_cars)
        for pad in self.all_boosts: pad.update(packet.game_boosts)

        self.kickoff = packet.game_info.is_round_active and packet.game_info.is_kickoff_pause

        if self.need_setup:
            for i in range(packet.num_cars):
                if i != self.index:
                    if packet.game_cars[i].team == self.team:
                        self.friends.append(carObject(i,packet.game_cars))
                    else:
                        self.foes.append(carObject(i,packet.game_cars))
            self.need_setup = False
