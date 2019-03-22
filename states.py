
from objects import *
from util import *
import time


"""
    if agent.me.airborn:
        yaw_to = math.atan2(lv[1],lv[0])
        yaw_adjust = cap(math.atan2(dv[1],dv[0]), -0.6, 0.6)
        pitch_to = math.atan2(lv[2],lv[0])
        roll_to = math.atan2(lv[1],lv[2])
        c.yaw = steerPD(yaw_to+yaw_adjust, -agent.me.rvel[2]/4.5)
        c.pitch = steerPD(pitch_to, agent.me.rvel[0]/4.5)
        c.roll = steerPD(roll_to, agent.me.rvel[1])
        return c
"""

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

def sa(agent,target,speed):
    c = agent.refresh()
    target_local = agent.me.matrix.dot(target-agent.me.location)
    vel_local = agent.me.matrix.dot(agent.me.velocity)
    direction = sign(target_local[1]) if abs(vel_local[1]) < 100 else sign(vel_local[1])

    c.steer,c.yaw,c.pitch,c.roll,angle = defaultPD(agent, target_local, True)

    c.throttle,c.boost = throttle(speed,)
    
    
    
    
    

def vc(agent,target,time):
    c = agent.refresh()
    lt = agent.me.matrix.dot(target-agent.me.location)
    lv = agent.me.matrix.dot(agent.me.velocity)
    d = lt.flatten().magnitude()

    speed = cap(d / time,0,2300)
        
    r = radius(lv[0])
    slowdown = (Vector3(0,sign(lt[0])*(r+40),0)-lt.flatten()).magnitude() / cap(r*1.5,1,1200)
    speed = cap(speed*slowdown,0,speed)
    s = math.atan2(lt[1],lt[0])
    c.steer = steerPD(s,0)
    c.yaw = steerPD(s,-agent.me.rvel[2]/4.5)
    c.pitch = steerPD(math.atan2(lt[2],lt[0]), agent.me.rvel[1]/5)
    up = agent.me.matrix.dot(Vector3(0,0,agent.me.location[2]))
    c.roll = steerPD(math.atan2(up[1],up[2]), agent.me.rvel[0]/5)
    if abs(lv[0]) < 250:
        c.throttle, c.boost = throttle(speed,lv[0],sign(lt[0]))
    else:
        c.throttle, c.boost = throttle(speed,lv[0],sign(lv[0]))        
        
    if (lv[0] < -150 and d > abs(2 * lv[0]) and abs(lt[0])/65 > abs(lt[1])) or agent.sinceJump <= 0.25:
        flip(agent,c,lt)
    return c

class atba:
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
    
    yaw = math.atan2(local[1],local[0])

    c.steer = steerPD(yaw,0)
    c.throttle, c.boost = throttle(speed,v[0])
    return c

    '''
    if agent.me.airborn:
        mag = airt.magnitude()
        if mag > 100:
            yaw = math.atan2(airt[1],airt[0])
            pitch = math.atan2(airt[2]*1.2,airt[0])
            roll = math.atan2(airt[1],airt[2]*1.2)
            c.yaw = steerPD(yaw, -agent.me.rvel[2]/4.5)
            c.pitch = steerPD(pitch, agent.me.rvel[1]/4.5)
            c.roll = steerPD(roll,agent.me.rvel[0])
            
            if abs(yaw) + abs(pitch) < 0.8:
                c.boost = True
            else:
                c.boost = False
            if agent.sinceJump < 0.15 and  airt[2] > 100:
                c.jump = True
                c.yaw = c.pitch = c.roll = 0
            elif agent.sinceJump >= 0.15 and agent.sinceJump < 0.25:
                c.jump = False
            elif agent.sinceJump < 0.3 and airt[2] > 100:
                c.jump = True
                c.yaw = c.pitch = c.roll = 0
            else:
                c.jump = False
        else:
            local = agent.me.matrix.dot(target.location-agent.me.location)
            yaw = math.atan2(airt[1],airt[0])
            pitch = math.atan2(airt[2],airt[0])
            c.yaw = steerPD(yaw, -agent.me.rvel[2]/4.5)
            c.pitch = steerPD(pitch, agent.me.rvel[1]/4.5)
            c.jump = False
            c.boost = False
        return c
    '''
    
        
