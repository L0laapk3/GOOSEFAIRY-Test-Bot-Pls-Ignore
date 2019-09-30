from objects import Vector3, Matrix3, shotObject
import math

BEST_180_SPEED = 1000

def defaultPosession(agent,car):
    relative = agent.ball.location-car.location
    vector,distance = relative.normalize(True)
    velocity = vector.dot(car.velocity)
    ball_kinetic = -agent.ball.velocity.dot(vector)/4
    car_kinetic = cap(velocity,abs(velocity)/2, 2300)/2
    potential = car.boost * 10
    total = ball_kinetic + potential + car_kinetic
    return int(total - (distance))

def shotConeRatio(car,ball_location,target_start,target_stop=None):
    #returns a number between -10.0 and 10.0
    #-10.0 means you are in the center of your shot cone
    #-0.5 is still dangerous, but anything higher means you're too off-sides to take a shot
    relative = (ball_location-car.location)
    if target_stop != None:
        shot_vector = bestShotVector(car,ball_location,target_start,target_stop)
    else:
        shot_vector = (target_start - ball_location).normalize()
    projection_distance = (relative).dot(shot_vector)
    cross_vector = shot_vector.cross([0,0,1])
    cross_distance = (relative).dot(cross_vector)
    if cross_distance != 0.0:
        return cap(-projection_distance / abs(cross_distance),-10.0,10.0)
    else:
        return cap(-projection_distance,-10.0,10.0)
    
def backsolve(target,agent,time):
    d = target-agent.me.location
    dx = (2* ((d[0]/time)-agent.me.velocity[0]))/time
    dy = (2* ((d[1]/time)-agent.me.velocity[1]))/time
    dz = (2 * ((325*time)+((d[2]/time)-agent.me.velocity[2])))/time
    return Vector3(dx,dy,dz)

def bestShotVector(car,ball_location,target_start,target_stop):
    relative = (ball_location-car.location)
    if target_stop != None:
        left_post_vector = target_start-ball_location
        right_post_vector = target_stop-ball_location
        return (relative).clamp(left_post_vector,right_post_vector).normalize()
    return relative.normalize()

def cap(x, low, high):
    if x < low:
        return low
    elif x > high:
        return high
    else:
        return x

def defaultPD(agent, local, direction = 0):
    #to reverse, multiply local by -1.0 and agent.c.steer by -1.0
    yaw = math.atan2(local[1],local[0])
    turn = (math.pi * direction) + yaw if direction != 0 else yaw
    up =  agent.me.matrix.dot(Vector3(0,0,1))
    target = [math.atan2(up[1],up[2]), math.atan2(local[2],local[0]), turn]
    agent.c.steer = steerPD(turn, 0)
    agent.c.yaw = steerPD(target[2],-agent.me.rvel[2]/4)
    agent.c.pitch = steerPD(target[1],agent.me.rvel[1]/4)
    agent.c.roll = steerPD(target[0],agent.me.rvel[0]/2.5)
    return target

def defaultThrottle(agent,target_speed,direction=1):
    agent_speed = agent.me.matrix.dot(agent.me.velocity)[0]
    final = ((target_speed * direction) - agent_speed)
    agent.c.throttle = cap(final*final*sign(final)/1000,-1.0,1.0)
    agent.c.boost = True if (final > 150 and agent_speed < 2250 and agent.c.throttle >= 1.0) else False
    return agent_speed
  
def field(point,radius):
    point = Vector3(abs(point[0]),abs(point[1]),abs(point[2]))
    if point[0] > 3860 - radius:
        return False
    elif point[1] > 5800 - radius:
        return False
    elif point[0] > 820 - radius and point[1] > 4950 - radius:
        return False
    elif point[0] > 2800 - radius and point[1] > -point[0] + 7750 - radius:
        return False
    return True    
    
def radius(v):
    return 139.059 + (0.1539 * v) + (0.0001267716565 * v * v)

def shotFinder(agent,target_start, target_stop=None):
    shots = []
    struct = agent.get_ball_prediction_struct()
    for i in range(18,struct.num_slices,18):
        intercept_time = struct.slices[i].game_seconds
        time_remaining = intercept_time - agent.time
        temp = struct.slices[i].physics.location
        ball = Vector3(temp.x,temp.y,temp.z)
        car_to_ball = (agent.ball.location - agent.me.location).flatten()
        angle = car_to_ball.angle(agent.me.matrix[0])
        time_remaining -= angle*0.446
        if time_remaining > 0.0:
            if (ball-agent.me.location).magnitude() / time_remaining < 2250:        
                ratio = shotConeRatio(agent.me,ball,target_start,target_stop)
                if ball[2] > 200 and ratio < -2.0 and agent.me.boost > (ball[2]/10):
                    shot_vector = bestShotVector(agent.me,ball,target_start,target_stop)
                    intercept = ball - (93*shot_vector)
                    shots.append(shotObject(intercept,shot_vector,intercept_time,ratio))
                elif ball[2] <= 200 and ratio < -0.5:
                    shot_vector = bestShotVector(agent.me,ball,target_start,target_stop)
                    intercept = ball - (93*shot_vector)
                    shots.append(shotObject(intercept,shot_vector,intercept_time,ratio))                 
    return shots

def side(x):
    if x <= 0:
        return -1
    return 1

def sign(x):
    if x < 0:
        return -1
    elif x == 0:
        return 0
    else:
        return 1

def steerPD(angle,rate):
    final = ((35*(angle+rate))**3)/10
    return cap(final,-1,1)
