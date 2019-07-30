from objects import *
from util import *
        

class vector_shot_test:
    def __init__(self):
        self.point = None
        self.time = None
        
    def execute(self,agent):
        if self.point == None:
            predict = agent.get_ball_prediction_struct()
            for i in range(300,predict.num_slices-1, 10):
                temp_time = predict.slices[i].game_seconds
                loc = predict.slices[i].physics.location
                temp_target = Vector3(loc.x,loc.y,loc.z)
                if temp_target[2] > 500:
                    vector = (Vector3(0,5100*-side(agent.team),0) -temp_target).normalize()
                    self.point = temp_target-(vector*100)
                    self.time = temp_time
                    break
            if self.point == None:
                self.point = Vector3(0,4500*side(agent.team),90)
                self.time = agent.time+10

            local_time = self.time-agent.time
            vector = (Vector3(0,5100*-side(agent.team),0) - self.point).normalize()
            return vector_shot(agent,self.point,vector,local_time)
        else:
            vector = (Vector3(0,5100*-side(agent.team),0) - self.point).normalize()
            local_time = self.time-agent.time
            if local_time < -0.5:
                self.point = None
                self.time = None
                return agent.c
            else:
                return vector_shot(agent,self.point,vector,local_time)

def vector_shot(agent,target,vector,time,speed=0):
    #Target point to hit
    #Vector to hit it in
    #time till it must be hit
    agent.renderer.begin_rendering("c")
    time = cap(time,0.001,10)
    if agent.sinceJump < 1.0 or agent.me.airborne == True:
        aerial(agent,target,time)
    else:
        distance_to_target = (target - agent.me.location).flatten().magnitude()
        velocity_local = agent.me.matrix.dot(agent.me.velocity)
        velocity_target = distance_to_target / time
        defaultThrottle(agent, velocity_target, velocity_local[0])
        height = (target-agent.me.location)[2]
        height_velocity = height / time
        if height_velocity*4.0 > velocity_target:
            local_drive_target = agent.me.matrix.dot(target-agent.me.location)
            angles = defaultPD(agent,local_drive_target)
            fly_target = backsolve(target,agent,time)
            if distance_to_target < 1500 and fly_target.magnitude() < 1000*time:
                agent.sinceJump = 0.0
                agent.jumps = 0
            elif abs(angles[2])<0.15:
                agent.jumps = 0
                agent.sinceJump = 0.0   
        else:
            drive_target = target - (vector * (distance_to_target/2))
            local_drive_target = agent.me.matrix.dot(drive_target - agent.me.location)
            angles = defaultPD(agent, local_drive_target)
            agent.c.boost = False if abs(angles[2]) > 1.57 else agent.c.boost
   
    agent.renderer.draw_rect_3d(target,10,10, True, agent.renderer.create_color(255,255,0,0))
    agent.renderer.end_rendering()
    return agent.c
