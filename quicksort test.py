x = [1, 3, 5, 7, 9, 11, 13]
y = 6


mi = 0
ma = len(x)-1

while len(x[mi:ma+1]) > 2:
    if x[(ma+mi)//2] > y:
        ma = (ma+mi)//2
    else:
        mi = (ma+mi)//2

print(mi,ma)
