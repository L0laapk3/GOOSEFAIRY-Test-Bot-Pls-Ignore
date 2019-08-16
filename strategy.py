from util import *
from objects import Vector3
import math

#These utils return information that is useful for strategic purposes

def defaultPosession(agent,car):
    relative = agent.ball.location-car.location
    vector,distance = relative.normalize(True)
    velocity = vector.dot(car.velocity)
    ball_kinetic = -agent.ball.velocity.dot(vector)/4
    car_kinetic = cap(velocity,abs(velocity)/2, 2300)/2
    potential = car.boost * 10
    total = ball_kinetic + potential + car_kinetic
    return int(total - (distance))

def shotConeRatio(agent,car,ball_location,posts = True):
    #returns a number between -10.0 and 10.0
    #-10.0 means you are in the center of your shot cone
    #-0.5 is still dangerous, but anything higher means you're too off-sides to take a shot
    relative = (ball_location-car.location)
    if posts:
        shot_vector = bestShotVector(car,ball_location)
    else:
        shot_vector = (Vector3(0,5100*car.team,100)-ball_location).normalize()
    projection_distance = (relative).dot(shot_vector)
    cross_vector = shot_vector.cross([0,0,1])
    cross_distance = (relative).dot(cross_vector)
    #agent.gui.line(ball_location,left_post,(255,235,175,0))
    #agent.gui.line(ball_location,right_post,(255,0,175,235))
    #agent.gui.line(ball_location, ball_location + (shot_vector*2000),(255,255,0,255))
    if cross_distance != 0.0:
        return cap(-projection_distance / abs(cross_distance),-10.0,10.0)
    else:
        return cap(-projection_distance,-10.0,10.0)
