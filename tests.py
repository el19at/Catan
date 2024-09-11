points = {}
points[(1, 5), (8, 2)] = 4
a = [(1, 5), (8, 2)]
for num in str(a)[2:-2].split('), ('):
    print(num)
"""
a = {str(k): v for k, v in points.items()}
b = {set([(int(k[2:-2].split(', ')[0]), int(k[2:-2].split(', ')[1]))]) : v for k, v in a.items()}
print(b)
"""