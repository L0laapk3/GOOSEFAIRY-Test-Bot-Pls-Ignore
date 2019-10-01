import math

class carObject:
    def __init__(self, index, game_cars = None):
        self.location = Vector3(0,0,0)
        self.velocity = Vector3(0,0,0)
        self.matrix = Matrix3([0,0,0])
        self.rvel = Vector3(0,0,0)
        self.team = 0
        self.boost= 0
        self.airborne = False
        self.index = index
        if game_cars != None:
            self.update(game_cars)

    def update(self, game_cars):
        car = game_cars[self.index]
        self.location.data = [car.physics.location.x, car.physics.location.y, car.physics.location.z]
        self.velocity.data = [car.physics.velocity.x, car.physics.velocity.y, car.physics.velocity.z]
        self.matrix = Matrix3( [car.physics.rotation.pitch, car.physics.rotation.yaw, car.physics.rotation.roll])
        self.rvel.data = self.matrix.dot([car.physics.angular_velocity.x, car.physics.angular_velocity.y, car.physics.angular_velocity.z])
        self.team = car.team
        self.boost = car.boost
        self.airborne = not car.has_wheel_contact

class ballObject:
    def __init__(self):
        self.location = Vector3(0,0,0)
        self.velocity = Vector3(0,0,0)
        
    def update(self,ball):
        self.location.data = [ball.physics.location.x, ball.physics.location.y, ball.physics.location.z]
        self.velocity.data = [ball.physics.velocity.x, ball.physics.velocity.y, ball.physics.velocity.z]

class boostObject:
    def __init__(self,index,location,is_large):
        self.index = index
        self.location = Vector3(location.x,location.y,location.z)
        self.active = True
        self.is_large = is_large
    def update(self,game_boosts):
        self.active = game_boosts[self.index].is_active

class shotObject:
    def __init__(self,intercept,vector,time,ratio):
        self.intercept = intercept
        self.vector = vector
        self.intercept_time = time
        self.ratio = ratio
    def render(self,agent):
        agent.gui.star(self.intercept,(255,255,255,255))
        color = (255,255,0,255)
        agent.gui.line(self.intercept-(self.vector*1000),self.intercept+(self.vector*1000),color)
        
class goalObject:
    def __init__(self,team):
        team = 1 if team == 1 else -1
        self.location = Vector3(0,team * 5150,0)
        self.left_post = Vector3(-team * 720,team * 5150,0)
        self.right_post = Vector3(team * 720,team * 5150,0)
        
class Matrix3:
    def __init__(self,r):
        CR = math.cos(r[2])
        SR = math.sin(r[2])
        CP = math.cos(r[0])
        SP = math.sin(r[0])
        CY = math.cos(r[1])
        SY = math.sin(r[1])        
        self.data = [Vector3(CP*CY, CP*SY, SP),Vector3(CY*SP*SR-CR*SY, SY*SP*SR+CR*CY, -CP * SR),Vector3(-CR*CY*SP-SR*SY, -CR*SY*SP+SR*CY, CP*CR)]
    def __getitem__(self,key):
        return self.data[key]
    def dot(self,vector):
        return Vector3(self.data[0].dot(vector),self.data[1].dot(vector),self.data[2].dot(vector))

class lineRequest:
    def __init__(self,start,end,color):
        self.start = start
        self.end = end
        self.color = color
    def render(self,agent,enable):
        agent.renderer.draw_line_3d(self.start,self.end,agent.renderer.create_color(*self.color))
        if enable:
            agent.gui.draw_line(self.start,self.end,self.color)
        
class rectRequest:
    def __init__(self,location,width,height,fill,color,center=True):
        self.location = location
        self.width = width
        self.height = height
        self.fill = fill
        self.center = center
        self.color = color
    def render(self,agent,enable):
        if self.center:
            location = self.location - Vector3(self.width,self.height,0)
        else:
            location = self.location
        agent.renderer.draw_rect_3d(location,self.width,self.height,self.fill,agent.renderer.create_color(*self.color))
        if enable:
            if self.center:
                agent.gui.draw_rect(location,self.width,self.height,self.fill,self.color)
            else:
                agent.gui.draw_rect(location,self.width,self.height,self.fill,self.color)
     
class stringRequest:
    def __init__(self,location,scale,text,color):
        self.location = location
        self.scale = scale
        self.text = text
        self.color = color
    def render(self,agent,enable):
        agent.renderer.draw_string_2d(self.location[0],self.location[1],self.scale[0],self.scale[1],self.text,self.color)

class Vector3:
    def __init__(self, *args):
        self.data = args[0] if isinstance(args[0],list) else [x for x in args]
    def __getitem__(self,key):
        return self.data[key]
    def __setitem__(self,key,value):
        self.data[key] = value
    def __str__(self):
        return str(self.data)
    def __add__(self,value):
        return Vector3(self[0]+value[0], self[1]+value[1], self[2]+value[2])
    def __sub__(self,value):
        return Vector3(self[0]-value[0],self[1]-value[1],self[2]-value[2])
    def __mul__(self,value):
        return Vector3(self[0]*value, self[1]*value, self[2]*value)
    __rmul__ = __mul__
    def __div__(self,value):
        return Vector3(self[0]/value, self[1]/value, self[2]/value)
    def magnitude(self):
        return math.sqrt((self[0]*self[0]) + (self[1] * self[1]) + (self[2]* self[2]))
    def normalize(self,returnMag=False):
        mag = self.magnitude()
        if mag != 0:
            if returnMag:
                return Vector3(self[0]/mag, self[1]/mag, self[2]/mag),mag
            else:
                return Vector3(self[0]/mag, self[1]/mag, self[2]/mag)
        else:
            if returnMag:
                return Vector3(0,0,0),0
            else:
                return Vector3(0,0,0)
    def dot(self,value):
        return self[0]*value[0] + self[1]*value[1] + self[2]*value[2]
    def cross(self,value):
        return Vector3((self[1]*value[2]) - (self[2]*value[1]),(self[2]*value[0]) - (self[0]*value[2]),(self[0]*value[1]) - (self[1]*value[0]))
    def flatten(self):
        return Vector3(self[0],self[1],0)
    def render(self):
        return [self[0],self[1]]
    def copy(self):
        return Vector3(self.data[:])
    def angle(self,value):
        return math.acos(self.normalize().dot(value.normalize()))
    def clamp(self,start,end):
        if self.side(start) >= 0:
            if self.side(end) <= 0 :
                return self
            else:
                return end
        else:
            return start
    def side(self,value):
        temp = self.cross([0,0,1]).dot(value)
        if temp > 0:
            return 1
        elif temp == 0:
            return 0
        else:
            return -1
    
