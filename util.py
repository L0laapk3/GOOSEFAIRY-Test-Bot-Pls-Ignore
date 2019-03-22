from objects import Vector3, Matrix3, Line

def backsolve(a,b,time):
    d = b-a.location
    dx = (2* ((d[0]/time)-a.velocity[0]))/time
    dy = (2* ((d[1]/time)-a.velocity[1]))/time
    dz = (2 * ((325*time)+((d[2]/time)-a.velocity[2])))/time
    return Vector3(dx,dy,dz)

def cap(x, low, high):
    if x < low:
        return low
    elif x > high:
        return high
    else:
        return x

def defaultPD(agent, local, angle = False):
    turn = math.atan2(local[1],local[0])
    steer = steerPD(turn,0)
    yaw = steerPD(turn,-agent.me.rvel[2]/5)
    pitch = steerPD(math.atan2(local[2],local[0]),agent.me.rvel[1]/5)
    roll = steerPD(math.atan2(agent.me.matrix.data[2][1],agent.me.matrix.data[2][2]),agent.me.rvel[0]/5)
    if angle == False:
        return steer,yaw,pitch,roll
    else:
        return steer,yaw,pitch,roll,turn
    
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
    pitch = -sign(local[1])
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
    final = ((35*(angle+rate))**3)/20
    return cap(final,-1,1)

def throttle(target_speed, agent_speed, direction = 1):
    final = ((abs(target_speed) - abs(agent_speed))/100) * direction
    if final > 1.5:
        boost = True
    else:
        boost = False
    if final > 0 and target_speed > 1400:
        final = 1
        
    return cap(final,-1,1),boost
