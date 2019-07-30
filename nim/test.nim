import math

proc rename(x:float): float {.exportc, dynlib .} = 
    return arccos(x)

proc nim_add(a:int,b:int): int {.exportc, dynlib .} =
    return a+b
    