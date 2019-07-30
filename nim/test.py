
import math




#test_lib.nim_add.argtypes = [c_int, c_int]
#test_lib.nim_add.restype = c_int
from ctypes import *
import time
import random

test_lib = CDLL("test.dll")
test_lib.rename.argtypes = [c_float]
test_lib.rename.restype = c_float

start = time.perf_counter()
for i in range(1000000):
    a = math.acos(0.5)
print(time.perf_counter()-start)

start = time.perf_counter()
for i in range(1000000):
    a = test_lib.rename(0.5)
print(time.perf_counter()-start)



#print(test_lib.nim_add(99,1))


