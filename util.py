from objects import Vector3, Matrix3, Line
import math

BEST_180_SPEED = 1000

def aerial(agent, target, time):
    before = agent.c.jump
    dv_target = backsolve(target,agent,time)
    dv_total = dv_target.magnitude()
    dv_local = agent.me.matrix.dot(dv_target)
    angles = defaultPD(agent,dv_local)

    precision = cap((dv_total/1500),0.05, 0.60)

    if dv_local[2] > 100  or agent.me.airborne == False:
        if agent.sinceJump < 0.3:
            agent.c.jump = True
        elif agent.sinceJump >= 0.32:
            agent.c.jump = True
            agent.c.pitch = agent.c.yaw = agent.c.roll = 0
        else:
            agent.c.jump = False
    else:
        agent.c.jump = False

    if dv_total > 40:
        if abs(angles[1])+abs(angles[2]) < precision:
            agent.c.boost = True
        else:
            print(abs(angles[1])+abs(angles[2]), precision)
            agent.c.boost = False
    else:
        fly_target = agent.me.matrix.dot(target - agent.me.location)
        angles = defaultPD(agent,fly_target)
        agent.c.boost = False
    
    
def backsolve(target,agent,time):
    d = target-agent.me.location

    dx = (2* ((d[0]/time)-agent.me.velocity[0]))/time
    dy = (2* ((d[1]/time)-agent.me.velocity[1]))/time
    dz = (2 * ((325*time)+((d[2]/time)-agent.me.velocity[2])))/time
    return Vector3(dx,dy,dz)

def cap(x, low, high):
    if x < low:
        return low
    elif x > high:
        return high
    else:
        return x

def defaultPD(agent, local, direction = 0):
    turn = math.atan2(local[1],local[0])
    turn = (math.pi * direction) + turn if direction != 0 else turn
    up =  agent.me.matrix.dot(Vector3(0,0,agent.me.location[2]))
    temp = [math.atan2(up[1],up[2]), math.atan2(local[2],local[0]), turn]
    target = temp#retargetPD(agent.me.rvel, temp)
    agent.c.steer = steerPD(turn, 0)
    agent.c.yaw = steerPD(target[2],-agent.me.rvel[2]/4)
    agent.c.pitch = steerPD(target[1],agent.me.rvel[1]/4)
    agent.c.roll = steerPD(target[0],agent.me.rvel[0]/2.5)
    return temp

def retargetPD(rvel,target):
    return Vector3([sign(target[x]) * (2*math.pi - abs(target[x])) if sign(rvel[x]) == sign(target[x]) and (2*math.pi - abs(target[x]))/cap(abs(rvel[x]),0.001,99) > (abs(target[x])*2/cap(abs(rvel[x]),0.001,99)) else target[x] for x in range(3)])
    
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

def flip(agent,c,local):
    #assumes controller will handle recovery
    pitch = -sign(local[0])
    if not agent.me.airborn:
        c.jump = True
        agent.sinceJump = 0
    if agent.sinceJump <= 0.05:
        c.jump = True
        c.pitch = pitch
    elif agent.sinceJump > 0.05 and agent.sinceJump <= 0.1:
        c.jump = False
        c.pitch = pitch
    elif agent.sinceJump > 0.1 and agent.sinceJump <= 0.13:
        c.jump = True
        c.pitch = pitch
        c.roll = 0
        c.yaw = 0

def radius(v):
    return 139.059 + (0.1539 * v) + (0.0001267716565 * v * v)

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

def defaultThrottle(agent,target_speed,agent_speed,direction=1):
    final = abs(target_speed) - abs(agent_speed) * direction
    if final >= 0.0:
        agent.c.throttle = 1.0
        if agent_speed < 2250:
            agent.c.boost = True
    elif final < -100.0:
        agent.c.throttle = -1.0
    else:
        agent.c.throttle = 0.5

def throttle(target_speed, agent_speed, direction = 1):
    final = ((abs(target_speed) - abs(agent_speed))/100) * direction
    if final > 1.5 or (final >0 and target_speed > 1410):
        boost = True
    else:
        boost = False
    if final > 0 and target_speed > 1410:
        final = 1
    return cap(final,-1,1),boost
