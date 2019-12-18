from objects import Vector3, Matrix3
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
    #returns a number between -10.0 and 10.0, the vector to shoot along, and an offset ratio
    #-10.0 means you are in the center of your shot cone
    #-0.5 is still dangerous, but anything higher means you're too off-sides to take a shot
    relative = (ball_location-car.location)
    centerline = target_start+target_stop
    if target_stop != None:
        shot_vector = bestShotVector(car,ball_location,target_start,target_stop)
    else:
        shot_vector = (target_start - ball_location).normalize()
    
    projection_distance = (relative).dot(shot_vector)
    cross_vector = shot_vector.cross([0,0,1])
    cross_distance = (relative).dot(cross_vector)
    offset_ratio = shot_vector.angle(centerline) / math.pi 
    if cross_distance != 0.0:
        return cap(-(projection_distance) / abs(cross_distance),-10.0,10.0),shot_vector,offset_ratio
    else:
        return cap(-projection_distance,-10.0,10.0),shot_vector,offset_ratio
    
def backsolve(target,agent,time):
    d = target-agent.me.location
    dx = (2* ((d[0]/time)-agent.me.velocity[0]))/time
    dy = (2* ((d[1]/time)-agent.me.velocity[1]))/time
    dz = (2 * ((325*time)+((d[2]/time)-agent.me.velocity[2])))/time
    return Vector3(dx,dy,dz)

def bestShotVector(car,ball_location,target_start,target_stop):
    relative = (ball_location-car.location)
    if target_stop != None:
        left_post_vector = (target_start-ball_location)
        right_post_vector = (target_stop-ball_location)
        return relative.clamp(left_post_vector,right_post_vector).normalize()
    return (target_start-ball_location).normalize()

def cap(x, low, high):
    if x < low:
        return low
    elif x > high:
        return high
    else:
        return x

def defaultPD(agent, local, direction = 1.0):
    #to reverse, multiply local by -1.0 and agent.c.steer by -1.0
    local *= direction
    up =  agent.me.matrix.dot(Vector3(0,0,1))
    target = [math.atan2(up[1],up[2]), math.atan2(local[2],local[0]), math.atan2(local[1],local[0])]
    agent.c.steer = steerPD(target[2], 0) * direction
    agent.c.yaw = steerPD(target[2],-agent.me.rvel[2]/4) * direction
    agent.c.pitch = steerPD(target[1],agent.me.rvel[1]/4) * direction
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

def hitboxDist(angle):
    x = math.cos(abs(angle))
    y = math.sin(abs(angle))
    return (x*73) + (y*42)
    
def radius(v):
    return 139.059 + (0.1539 * v) + (0.0001267716565 * v * v)

def shotValid(slices, shot):
    mi = 0
    ma = len(slices)-1
    while len(slices[mi:ma+1]) > 2:
        if slices[(ma+mi)//2].game_seconds > shot.intercept_time:
            ma = (ma+mi)//2
        else:
            mi =(ma+mi)//2
    dt = slices[ma].game_seconds - slices[mi].game_seconds
    time_from_mi = shot.intercept_time-slices[mi].game_seconds
    mi = slices[mi].physics.location
    ma = slices[ma].physics.location
    slopes = Vector3(ma.x-mi.x,ma.y-mi.y,ma.z-mi.z) * (1 / dt)
    slice_intercept = Vector3(mi.x,mi.y,mi.z) + (slopes * time_from_mi)
    if (shot.ball - slice_intercept).magnitude() > 30:
        return False
    return True

def side(x):
    if x <= 0:
        return -1
    return 1

def soonest(x):
    soonest = x[0]
    for item in x:
        if item.intercept_time < soonest.intercept_time:
            soonest = item
    return soonest

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
