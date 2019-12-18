from util import *
from objects import Vector3

class routine:
    def __init__(self):
        pass
    def run(self,agent):
        agent.stack.pop()

class simpleBoost(routine):
    def __init__(self,boost):
        self.boost = boost
    def run(self,agent):
        relative = self.boost.location - agent.me.location
        distance = (relative).magnitude()
        local = agent.me.matrix.dot(relative)
        angles = defaultPD(agent, local)
        speed = defaultThrottle(agent,2300)
        if abs(angles[2]) > 1.0:
            agent.c.handbrake = True
        if speed > 750 and not agent.me.airborne and distance / speed > 2.0 and abs(angles[2]) <= 0.12:
            agent.stack.append(flip(local))
        if not self.boost.is_large or agent.me.airborne:
            agent.c.boost = False
        if not self.boost.active or agent.me.boost > 99:
            agent.stack.pop()
        if distance/cap(speed,0.01,2400) < 0.1:
            agent.c.handbrake = True
            defaultPD(agent, agent.me.matrix.dot(agent.ball.location-agent.me.location))
        agent.c.boost = False if abs(angles[2]) > 0.3 or agent.me.airborne else agent.c.boost
            
class kickoff(routine):
    def __init__(self):
        self.jumped = False
    def run(self,agent):
        main_target = agent.ball.location + ((agent.friend_goal.location-agent.ball.location).normalize()*150)
        relative = main_target-agent.me.location
        defaultPD(agent,agent.me.matrix.dot(relative))
        defaultThrottle(agent,2300)
        if relative.magnitude() < 600:
            agent.stack.pop()
            agent.stack.append(flip(agent.me.matrix.dot(agent.foe_goal.location-agent.me.location)))
        
class defend(routine):
    def __init__(self):
        self.step = 0
    def run(self,agent):
        relative = agent.ball.location-agent.friend_goal.location
        goal_to_ball = relative.normalize()
        distance = relative.magnitude()
        if self.step == 0:
            if distance > 1200:
                agent.stack.append(handbrakeTurn(agent.friend_goal,goal_to_ball))
            self.step = 1
        elif self.step == 1:
            projection_distance = (agent.me.location-agent.friend_goal.location).dot(goal_to_ball)
            target = agent.friend_goal.location + (goal_to_ball*(projection_distance/1.2))

def shotFinder(agent,target_start, target_stop=None):
    shots = []
    struct = agent.get_ball_prediction_struct()
    for i in range(10,struct.num_slices,10):
        intercept_time = struct.slices[i].game_seconds
        time_remaining = intercept_time - agent.time
        temp = struct.slices[i].physics.location
        ball = Vector3(temp.x,temp.y,temp.z)
        car_to_ball = (ball - agent.me.location)
        angle = min(car_to_ball.angle(agent.me.matrix[0]),car_to_ball.angle(-1*agent.me.matrix[0]))
        ratio = shotConeRatio(agent.me,ball,target_start,target_stop)
        time_remaining -= abs(angle)*0.318
        time_remaining -= abs(0.25 / cap(ratio,-10,-1))
        if abs(ball[1]) > 5200:
            break
        if time_remaining > 0.1 and (ball-agent.me.location).magnitude() / time_remaining < 2300:
            if car_to_ball[2] >= 280 and ratio < -2.0 and agent.me.boost > ((ball[2]-200)/20):
                shot_vector = bestShotVector(agent.me,ball,target_start,target_stop)
                shots.append(shot(ball,shot_vector,intercept_time,ratio))
            if car_to_ball[2] < 280 and ratio < -0.5:
                shot_vector = bestShotVector(agent.me,ball,target_start,target_stop)
                shots.append(shot(ball,shot_vector,intercept_time,ratio))             
    return shots
                
class shot(routine):
    def __init__(self,ball,vector,time,ratio,speed = 0):
        self.ball = ball
        self.intercept = ball - (vector.flatten()*93)
        self.vector = vector
        self.intercept_time = time
        self.ratio = ratio
        self.speed = speed #todo - make work
        
    def run(self,agent):
        raw_time_remaining = self.intercept_time-agent.time
        time_remaining = cap(raw_time_remaining,0.001,20.0)
        
        relative = self.intercept - agent.me.location
        local_target = agent.me.matrix.dot(relative)
        local_distance = local_target.flatten().magnitude()
        local_velocity = agent.me.matrix.dot(agent.me.velocity)
        velocity_target = local_distance / time_remaining
        direction = sign(local_target[0]) if abs(local_velocity[0]) < 1000 else sign(local_velocity[0])
        defaultThrottle(agent, velocity_target,direction)#todo-slow down for big turns
        drive_target = self.intercept - (self.vector * (local_distance/3))
        local_drive_target = agent.me.matrix.dot(drive_target - agent.me.location)
        angles = defaultPD(agent, local_drive_target,direction)
        local_fly_target = agent.me.matrix.dot(backsolve(self.intercept,agent,time_remaining))
        can_jump = True if local_fly_target.magnitude() / time_remaining < 1000 and agent.me.boost*30.03 > local_fly_target.magnitude()-600  else False
        
        if raw_time_remaining < -0.35 or velocity_target > 2500 or not shotValid(agent.get_ball_prediction_struct().slices,self):
            agent.stack.pop()
        elif (abs(angles[2])<0.25 or local_distance < 550) and self.intercept[2] >= 110 and time_remaining < local_target[2]/500:    
            agent.stack.pop()
            agent.stack.append(aerial(self.intercept,self,self.intercept_time))
        elif time_remaining < 0.35 and abs(angles[2]) < 0.15 and local_distance < 200:
            agent.stack.pop()
            t= 0.9 if direction == 1 else 0.3
            agent.stack.append(flip(agent.me.matrix.dot(self.vector),t))
      
        agent.c.boost = False if abs(angles[2]) > 0.3 or agent.me.airborne or direction == -1 else agent.c.boost
        agent.c.handbrake = True if abs(angles[2]) > 2.8 and direction == 1 else False
        self.render(agent)
    def render(self,agent):
        agent.gui.star(self.intercept,(255,255,255,255))
        agent.gui.line(self.intercept, self.intercept-(self.vector*1000), (255,255,255,255))
        
class aerial(routine):
    def __init__(self,target,shot,time):
        self.target = target
        self.shot = shot
        self.intercept_time = time
        self.jump_time = time
        self.double = False
        
    def run(self,agent):
        time_remaining = self.intercept_time - agent.time
        dv_target = backsolve(self.target,agent,time_remaining)
        dv_total = dv_target.magnitude()
        dv_local = agent.me.matrix.dot(dv_target)
        angles = defaultPD(agent,dv_local)
        precision = cap((dv_total/1000),0.05, 0.60)

        if time_remaining < -0.2 or (time_remaining > 0.5 and not shotValid(agent.get_ball_prediction_struct().slices,self.shot)):
            agent.stack.pop()
        elif time_remaining < 0.5 and self.double == False and abs(self.target[2]-agent.me.location[2]) < 120: #todo - change so that dodge happens sooner when car is at right height
            agent.stack.pop()
            agent.stack.append(flip(agent.me.matrix.dot(self.shot.vector)))

        if agent.me.airborne == False:
            if self.jump_time < 0.0:
                self.jump_time = agent.time
        elapsed = agent.time - self.jump_time
        if elapsed <= 0.2:
            agent.c.jump = True 
        elif elapsed >= 0.23 and dv_local[2] > 300:
            agent.c.jump = True
            self.double = True
            agent.c.pitch = 0
            agent.c.yaw = 0
            agent.c.roll = 0
        else:
            agent.c.jump = False

        if dv_total > 40:
            if abs(angles[1])+abs(angles[2]) < precision:
                agent.c.boost = True
            else:
                agent.c.boost = False
        else:
            fly_target = agent.me.matrix.dot(self.target - agent.me.location)
            angles = defaultPD(agent,fly_target)
            agent.c.boost = False

class flip(routine): #dodges in the desired vector
    def __init__(self, vector, cancel_time = 0.9):
        vector = vector.normalize()
        self.pitch = abs(vector[0])*-sign(vector[0])
        self.yaw = abs(vector[1]) * sign(vector[1])
        self.cancel_time = cancel_time
        self.time = -1
  
    def run(self,agent):
        if self.time == -1:
            elapsed = 0
            self.time = agent.time
        else:
            elapsed = agent.time-self.time
        if elapsed > 0.3 and not agent.me.airborne:
            agent.c.jump = False
            agent.stack.pop()
        elif elapsed < 0.1:
            agent.c.jump = True
        elif elapsed >=0.1 and elapsed < 0.16:
            agent.c.jump = False
        elif elapsed >= 0.16 and elapsed < self.cancel_time:
            agent.c.jump = True
            agent.c.pitch = self.pitch
            agent.c.yaw = self.yaw
        else:
            agent.c.jump = False
            agent.stack.pop()

class handbrakeTurn(routine):
    def __init__(self,target,vector):
        #drive towards the target and handbrake turn to face a direction
        self.target = target.flatten()
        self.vector = vector
        self.step = 0
    def run(self,agent):
        relative = self.target-agent.me.location.flatten()
        distance = (relative).magnitude()
        vector = relative.normalize()
        relative_velocity = vector.dot(agent.me.velocity)
        angle = abs(defaultPD(agent,agent.me.matrix.dot(self.vector))[2])
        turn_time = (angle/3.14)
        
        if turn_time > distance / cap(relative_velocity,50,2300) or self.step == 1 or distance < 200:
            self.step = 1
            defaultPD(agent,agent.me.matrix.dot(self.target+(self.vector*5000)-agent.me.location))
            agent.c.handbrake = True
            agent.c.throttle = 1.0
            if angle < 0.5:
                agent.stack.pop()
        else:
            defaultPD(agent,agent.me.matrix.dot(relative))
            defaultThrottle(agent,2300)
            agent.c.boost = False

class atba(routine):
    def run(self,agent):
        relative = agent.ball.location-agent.me.location
        local_target = agent.me.matrix.dot(relative)
        local_distance = local_target.magnitude()
        local_velocity = agent.me.matrix.dot(agent.me.velocity)
        if local_target[0] < 0.0  and (local_distance < 800 or local_distance > 2000):
            direction = -1
        else:
            direction = 1  
        angles = defaultPD(agent,local_target,direction)
        defaultThrottle(agent,1000,direction)

class goto(routine):
    def __init__(self,target):
        self.target = target
    def run(self,agent):
        relative = self.target-agent.me.location
        local = agent.me.matrix.dot(relative)
        angles = defaultPD(agent, local)
        speed = defaultThrottle(agent,2300)
        if speed > 700 and not agent.me.airborne and relative.magnitude() / speed > 1.8 and abs(angles[2]) <= 0.10 and agent.me.boost < 30:
            agent.stack.append(flip(local))
        if agent.me.airborne:
            agent.c.boost = False
        if relative.magnitude() < 350:
            agent.stack.pop()
        
        
            
        
