import math
import time
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.agents.base_agent import  SimpleControllerState
from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3 as vector3, Rotator

from objects import *
from routines import *
from graphics import *

class Gosling(BaseAgent):
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

        self.gui = gui(self,False) #True to enable GUI

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
        left = Vector3(-3200*side(self.team),self.ball.location[1]+(400*side(not self.team)),92)
        right = Vector3(3200*side(self.team),self.ball.location[1]+(400*side(not self.team)),92)
        shots = shotFinder(self,self.foe_goal.left_post, self.foe_goal.right_post)
        upfields = shotFinder(self,left,right)

        if len(self.stack) > 0:
            if isinstance(self.stack[-1], goto) and (len(upfields) > 0 or len(shots) > 0):
                self.stack = []
            elif isinstance(self.stack[-1],shot) and len(shots)>0 and self.stack[-1].intercept_time -0.6 > soonest(shots).intercept_time:
                self.stack = []
            
        if len(self.stack) < 1:
            if len(shots) > 0 and len(upfields) > 0 and (self.foes[0].location - self.ball.location).magnitude() < 1000:
                soonest_shot = soonest(shots)
                soonest_upfield = soonest(upfields)
                if soonest_shot.intercept_time < soonest_upfield.intercept_time:
                    self.stack.append(shot(soonest_shot))
                else:
                    self.stack.append(shot(soonest_upfield))                
            elif len(shots) > 0:
                self.stack.append(shot(soonest(shots)))
            elif len(upfields) > 0:
                self.stack.append(shot(soonest(upfields)))   
            elif self.me.boost < 50:                   
                our_boosts = [x for x in self.large_boosts if (x.location-self.friend_goal.location).magnitude() < 7000 and x.active]
                closest = our_boosts[0]
                for boost in our_boosts:
                    if (self.me.location-boost.location).magnitude() < (self.me.location-closest.location).magnitude():
                        closest = boost
                self.stack.append(simpleBoost(closest))
            else:
                self.stack.append(goto(self.friend_goal.location))

                

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
