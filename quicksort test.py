x = [1, 3, 5, 7, 9, 11, 13]
y = 14
while len(x) > 1:
    if x[len(x)//2] > y:
        x = x[:len(x)//2]
    else:
        x = x[len(x)//2:]
print(x)
