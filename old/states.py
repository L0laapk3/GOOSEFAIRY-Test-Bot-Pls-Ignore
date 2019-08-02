from objects import *
from util import *
import time


class shotMaker():
    def __init__(self,target,vector,time,flip = True):
        self.expired = False
        self.temp = 0
        self.target = target
        self.vector = vector
        self.time = time
        self.flip = flip
        
    def temp_finder(self,agent):
        self.temp = 0

        predict = agent.get_ball_prediction_struct()
        for i in range(10, predict.num_slices, 20):
            self.time = predict.slices[i].game_seconds
            time = self.time - agent.time
            loc = predict.slices[i].physics.location
            ball = Vector3(loc.x,loc.y,loc.z)

            self.vector = (ball.flatten()-Vector3(0,5100*-side(agent.team),0)).normalize()
            self.target = ball.flatten()+(self.vector*90)
            local = agent.me.matrix.dot(self.target-agent.me.location)
            current_speed = agent.me.matrix.dot(agent.me.velocity)[0]
            angle = math.atan2(local[1],local[0])
            
            distance_remaining = (self.target-agent.me.location).magnitude() + (400*angle)
            acceleration_time_needed = (2 * ((distance_remaining/time)-current_speed))/(time*1000)

            if acceleration_time_needed < time-1:
                break

    def execute(self,agent):
        time = cap(self.time - agent.time,0.001,10)
        if self.time - agent.time< -0.5:
            self.temp += 1
        projection = (agent.me.location - self.target).magnitude()#.dot(self.vector))
        #need to add additional distance to account for car rotation/shape
        drive_target = self.target + (self.vector * (projection/2)) #need to allow this ratio to adjust

        current_speed = agent.me.matrix.dot(agent.me.velocity)[0]
        available_acceleration_time = cap(agent.me.boost / 33.3,0,time)
        distance_remaining = (agent.me.location - self.target).magnitude() #need to add turn logic & distance math

        acceleration_time_needed = (2 * ((distance_remaining/time)-current_speed))/(time*1000)

        ratio = acceleration_time_needed/(available_acceleration_time + 0.5)
        
        
        drive_speed = current_speed + sign(ratio-1)*(100*ratio)
        agent.renderer.begin_rendering("b")
        agent.renderer.draw_rect_3d(self.target,10,10, True, agent.renderer.create_color(255,0,0,255))
        agent.renderer.draw_rect_3d(drive_target,10,10, True, agent.renderer.create_color(255,0,255,0))
        agent.renderer.end_rendering()
        
        return test(agent,drive_target,drive_speed)
              
        #return vc(agent, drive_target, time)
                
        

def shottarget(agent,target,vector):
    target_line = Line(agent.me.location, target)
    points = []
    current = agent.me.location
    #aerial_space = target[2]
    #jump_point = target - (vector * aerial_space)

class atba2:
    def __init__(self):
        self.expired = False
        self.target = None
        self.time = 0
    def execute(self,agent):
        time = self.time - agent.time
        if self.target == None or time <= 0.0:
            predict = agent.get_ball_prediction_struct()
            for i in range(1,predict.num_slices,20):
                self.time = predict.slices[i].game_seconds
                self.target = Vector3(predict.slices[i].physics.location.x,predict.slices[i].physics.location.y,predict.slices[i].physics.location.z)
                time = cap(self.time - agent.time,0.01,6)
                if ((self.target - agent.me.location).magnitude() * 2) / (time*time) < 2000:
                    break
        agent.renderer.begin_rendering("b")
        agent.renderer.draw_rect_3d(self.target,10,10, True, agent.renderer.create_color(255,0,0,255))
        agent.renderer.end_rendering()
        return vc(agent,self.target, time)

def vc(agent,target,time):
    c = agent.refresh()
    local_target = agent.me.matrix.dot(target-agent.me.location)
    local_velocity = agent.me.matrix.dot(agent.me.velocity)
    distance = local_target.flatten().magnitude()

    speed = cap(distance / time ,0,2300)
        
    r = radius(local_velocity[0])
    slowdown = (Vector3(0,sign(local_target[1])*(r+40),0)-local_target.flatten()).magnitude() / cap(r*1.5,1,1200)
    speed = cap(speed*slowdown,0,speed)
    angles = defaultPD(agent, local_target)
    if abs(local_velocity[0]) < 250:
        c.throttle, c.boost = throttle(speed,local_velocity[0],sign(local_target[0]))
    else:
        c.throttle, c.boost = throttle(speed,local_velocity[0],sign(local_velocity[0]))        
        
    if (local_velocity[0] < -150 and distance > abs(2 * local_velocity[0]) and abs(local_target[0])/65 > abs(local_target[1])) or agent.sinceJump <= 0.25:
        flip(agent,c,local_target)
    return c

class atbaTest:
    def __init__(self):
        self.expired = False
    def ready(self,agent):
        return True
    def execute(self,agent):
        target = Vector3(0,5100*side(agent.team),0)
        predict = agent.get_ball_prediction_struct()
        dist = (agent.me.location - agent.ball.location).magnitude()
        checks = int(59 / cap(2000/dist,59,600))
        for i in range(1,predict.num_slices,checks):
            time = cap(predict.slices[i].game_seconds - agent.time,0.1,6)
            location = Vector3(predict.slices[i].physics.location.x,predict.slices[i].physics.location.y,predict.slices[i].physics.location.z)
            airt = agent.me.matrix.dot(backsolve(agent.me,location,time))
            if airt.magnitude() < 800*time:
                break

        toTarget = Line(location, target)
        toBall = Line(agent.me.location,location)
        intercept = location - (toTarget.direction*(90+30))

        angle = math.acos(toTarget.direction.dot(-1*toBall.direction)) * sign(toBall.direction.dot(toTarget.direction.cross([0,0,1])))

        toint = (intercept-agent.me.location).normalize()
        todir = toTarget.direction.cross([0,0,1]) * sign(angle)

        final = (toint * 10) + (todir * angle * angle * 10)

        agent.renderer.begin_rendering("a")
        agent.renderer.draw_line_3d(agent.me.location,agent.me.location +toint *100,agent.renderer.create_color(255,0,0,255))
        agent.renderer.draw_line_3d(agent.me.location,agent.me.location +todir*100,agent.renderer.create_color(255,255,0,255))
        agent.renderer.draw_line_3d(agent.me.location,agent.me.location + final * 10,agent.renderer.create_color(255,0,255,0))
        agent.renderer.end_rendering()
        
        
        return test(agent,final+agent.me.location,500)


def test(agent,target,speed):
    c = agent.refresh()
    v = agent.me.matrix.dot(agent.me.velocity)
    local = agent.me.matrix.dot(target-agent.me.location)

    r = radius(v[0])
    circle = Vector3(0,sign(local[1])*(r+40),0)
    cool = (circle-local.flatten()).magnitude() / cap(r*1.7,1,1200)
    if cool < 0.5:
        c.handbrake = True
    else:
        c.handbrake = False
    speed = cap(speed*cool,0,speed)

    defaultPD(agent, local)
    
    c.throttle, c.boost = throttle(speed,v[0])
    return c
    
        
