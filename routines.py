from util import *
from objects import Vector3

class routine:
    def __init__(self):
        pass
    def run(self,agent):
        agent.stack.pop()

class kickoff(routine):
    def __init__(self):
        self.jumped = False
    def run(self,agent):
        main_target = agent.ball.location + ((agent.friend_goal-agent.ball.location).normalize()*150)
        relative = main_target-agent.me.location
        defaultPD(agent,agent.me.matrix.dot(relative))
        defaultThrottle(agent,2300)
        if relative.magnitude() < 600:
            agent.stack.pop()
            agent.stack.append(flip(agent.me.matrix.dot(agent.foe_goal-agent.me.location)))

class shot(routine):
    def __init__(self,target,vector,time,speed=0):
        self.target = target
        self.vector = vector
        self.intercept_time = time
        self.speed = speed
    def run(self,agent):
        time_remaining = cap(self.intercept_time-agent.time,0.001,20.0)
        distance_to_target = (self.target - agent.me.location).flatten().magnitude()            
        velocity_local = agent.me.matrix.dot(agent.me.velocity)
        velocity_target = distance_to_target / time_remaining #todo- factor in self.speed
        defaultThrottle(agent, velocity_target, velocity_local[0])#todo-slow down for big turns
        height_velocity = (self.target-agent.me.location)[2] / time_remaining #vel to reach height
        if height_velocity*2 >= velocity_target:
            local_drive_target = agent.me.matrix.dot(self.target-agent.me.location)
            angles = defaultPD(agent,local_drive_target)
            fly_target = backsolve(self.target,agent,time_remaining)
            if fly_target.magnitude() < 1000*time or abs(angles[2])<0.15:
                agent.stack.pop()
                agent.stack.append(aerial(self.target,self.intercept_time))
        else:
            drive_target = self.target - (self.vector * (distance_to_target/2))
            local_drive_target = agent.me.matrix.dot(drive_target - agent.me.location)
            angles = defaultPD(agent, local_drive_target)
            agent.c.boost = False if abs(angles[2]) > 1.57 else agent.c.boost
        
class aerial(routine):
    def __init__(self,target,time):
        self.target = target
        self.intercept_time = time
        self.jump_time = time
        
    def run(self,agent):
        time_remaining = self.intercept_time - agent.time
        dv_target = backsolve(self.target,agent,time_remaining)
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
            agent.c.pitch = agent.c.yaw = agent.c.roll = 0
        else:
            agent.c.jump = False

        if dv_total > 40:
            if abs(angles[1])+abs(angles[2]) < precision:
                agent.c.boost = True
            else:
                agent.c.boost = False
        else:
            fly_target = agent.me.matrix.dot(target - agent.me.location)
            angles = defaultPD(agent,fly_target)
            agent.c.boost = False
        if time_remaining < -0.25:
            agent.stack.pop()

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

class atba(routine):
    def run(self,agent):
        defaultPD(agent, agent.me.matrix.dot(agent.ball.location-agent.me.location))
        defaultThrottle(agent,10)
            
        
