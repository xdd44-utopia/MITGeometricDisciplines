import math
from Rhino.Geometry import Point3d

def frange(start, stop=None, step=None):
    # if set start=0.0 and step = 1.0 if not specified
    start = float(start)
    if stop == None:
        stop = start + 0.0
        start = 0.0
    if step == None:
        step = 1.0

    count = 0
    while True:
        temp = float(start + count * step)
        if step > 0 and temp >= stop:
            break
        elif step < 0 and temp <= stop:
            break
        yield temp
        count += 1

def normalizeV(v):
    v = map(lambda x : x / magnitudeV(v), v)
    return Point3d(v[0], v[1], v[2])

def magnitudeV(v):
    return math.sqrt(sum(x ** 2 for x in v))

def dotProduct(u, v):
    return sum(u[i] * v[i] for i in range(len(u)))

def crossProduct(u, v):
    return [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]