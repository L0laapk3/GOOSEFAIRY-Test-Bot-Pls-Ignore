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
        if speed > 700 and not agent.me.airborne and distance / speed > 2.5 and abs(angles[2]) <= 0.10:
            agent.stack.append(flip(local))
        if not self.boost.is_large or agent.me.airborne:
            agent.c.boost = False
        if not self.boost.active or agent.me.boost > 99:
            agent.stack.pop()

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
                
class shot(routine):
    def __init__(self,s,speed=0):
        self.s = s
        self.target = s.intercept
        self.vector = s.vector
        self.intercept_time = s.intercept_time
        self.speed = speed
    def run(self,agent):
        raw_time_remaining = self.intercept_time-agent.time
        time_remaining = cap(raw_time_remaining,0.001,20.0)
        relative = self.target - agent.me.location
        distance_to_target = (relative).flatten().magnitude()            
        velocity_local = agent.me.matrix.dot(agent.me.velocity)
        velocity_target = distance_to_target / time_remaining
        if self.speed != 0:
            correction = cap((velocity_target - self.speed)/2,-velocity_target,2300-velocity_target) #make this nicer
        else:
            correction= 0
        defaultThrottle(agent, velocity_target+correction)#todo-slow down for big turns

        if raw_time_remaining < -0.25 or velocity_target > 2400 or not shotValid(agent.get_ball_prediction_struct().slices,self.s):
            agent.stack.pop()
        elif time_remaining < cap(math.sqrt(cap(relative[2],1,6000)/450),0.5,100):
            local_drive_target = agent.me.matrix.dot(self.target-agent.me.location)
            angles = defaultPD(agent,local_drive_target)
            fly_target = backsolve(self.target,agent,time_remaining)
            if fly_target.magnitude() < 1050*time_remaining or abs(angles[2])<0.16:
                agent.stack.pop()
                agent.stack.append(aerial(self.target,self.s,self.intercept_time))
        else:
            drive_target = self.target - (self.vector * (distance_to_target/1.75))
            local_drive_target = agent.me.matrix.dot(drive_target - agent.me.location)
            angles = defaultPD(agent, local_drive_target)
            agent.c.boost = False if abs(angles[2]) > 1.57 else agent.c.boost
        self.render(agent)
    def render(self,agent):
        agent.gui.star(self.target,(255,255,255,255))
        agent.gui.line(self.target, self.target-(self.vector*1000), (255,255,255,255))
            
        
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
        if self.target[2] > 300:
            dv_target[2] *= 3
        dv_total = dv_target.magnitude()
        dv_local = agent.me.matrix.dot(dv_target)
        angles = defaultPD(agent,dv_local)
        precision = cap((dv_total/1000),0.05, 0.60)

        if agent.me.airborne == False:
            if self.jump_time < 0.0:
                self.jump_time = agent.time
        elapsed = agent.time - self.jump_time
        if elapsed <= 0.3:
            agent.c.jump = True 
        elif elapsed >= 0.32 and dv_local[2] > 500:
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

        if time_remaining < -0.25 or (time_remaining > 0.8 and not shotValid(agent.get_ball_prediction_struct().slices,self.shot)):
            agent.stack.pop()
        elif time_remaining < 0.4 and self.double == False and abs(self.target[2]-agent.me.location[2]) < 150: #todo - change so that dodge happens sooner when car is at right height
            agent.stack.pop()
            agent.stack.append(flip(agent.me.matrix.dot(self.shot.vector)))

class flip(routine): #dodges in the desired vector
    def __init__(self, vector):
        if vector[0] != 0:
            self.pitch = -math.cos(vector[1]/vector[0])
            self.yaw = math.sin(vector[1]/vector[0])
        else:
            self.pitch = -1
            self.yaw = sign(vector[1])
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
        elif elapsed >= 0.16 and elapsed < 0.9:
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
        defaultPD(agent, agent.me.matrix.dot(agent.ball.location-agent.me.location))
        defaultThrottle(agent,10)

class goto(routine):
    def __init__(self,target):
        self.target = target
    def run(self,agent):
        relative = self.target-agent.me.location
        defaultPD(agent, agent.me.matrix.dot(relative))
        defaultThrottle(agent,700)
        if relative.magnitude() < 500:
            agent.stack.pop()
        
        
            
        
