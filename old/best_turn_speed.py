import math
import matplotlib.pyplot as plt

def radius(v):
    return 139.059 + (0.1539 * v) + (0.0001267716565 * v * v)

def distance(r):
    return math.pi*r


fig,ax = plt.subplots()

x=[]
y=[]
total = 0
counter = 0
for v in range(350,2300):
    r = radius(v)
    d = distance(r)
    time = d/v
    total += time
    counter += 1
    x.append(v)
    y.append(time)
print(total / counter)
ax.plot(x,y)
ax.set(xlabel="velocity",ylabel="time",title="time to complete a 180 degree turn")
plt.show()



#for i in range(100,2000,100):
 #   print(i*2/( distance(i)/2))
