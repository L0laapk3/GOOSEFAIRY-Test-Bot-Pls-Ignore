import math


def dist(angle):
    x = math.cos(abs(angle))
    y = math.sin(abs(angle))
    return (x*73) + (y*42) + 93


