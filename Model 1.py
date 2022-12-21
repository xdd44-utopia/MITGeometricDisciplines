from ast import Delete
from Rhino.Geometry import NurbsSurface, Polyline, Point3d
import rhinoscriptsyntax as rs
import scriptcontext as sc
from math import *

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

def x1(u, v):
    u += v
    return cos(5 * u) / 10 + sin(v) * cos(u)

def y1(u, v):
    u += v
    return sin(5 * u) / 10 + sin(v) * sin(u)

def z1(u, v):
    return cos(v)

def scale(x, y, z, u, v):
    return offset - sqrt(pow(x(u, v), 2) + pow(y(u, v), 2) + pow(z(u, v), 2) / 2)

def x2(u, v):
    u += v
    return sin(v) * pow(cos(u), 3) * 0.96

def y2(u, v):
    u += v
    return sin(v) * pow(sin(u), 3) * 0.96

def z2(u, v):
    return cos(v)
    
ustep = pi / 32
vstep = pi / 32

def generate(x, y, z, ustep, vstep):

    for i, u in enumerate(frange(0, pi * 2, ustep)):
        for j, v in enumerate(frange(0, pi, vstep)):

            if (v <= vstep * 5 or v > pi - vstep * 7):
                continue

            cur = Point3d(x(u, v), x(u, v), z(u, v))
            uu = u + ustep
            vv = v
            nex = Point3d(x(uu, vv), x(uu, vv), z(uu, vv))
            segment = Polyline((cur, nex))
            # sc.doc.Objects.AddPolyline(segment)

            if (j % 2 == 0):
                if (i % 2 == 0):
                    triangle = NurbsSurface.CreateFromCorners(
                        Point3d(x(u, v), y(u, v), z(u, v)),
                        Point3d(x(u + ustep, v), y(u + ustep, v), z(u + ustep, v)),
                        Point3d(x(u, v + vstep) * scale(x, y, z, u, v + vstep), y(u, v + vstep) * scale(x, y, z, u, v + vstep), z(u, v + vstep))
                    )
                    sc.doc.Objects.AddSurface(triangle)
                    triangle = NurbsSurface.CreateFromCorners(
                        Point3d(x(u, v), y(u, v), z(u, v)),
                        Point3d(x(u - ustep, v), y(u - ustep, v), z(u - ustep, v)),
                        Point3d(x(u, v + vstep) * scale(x, y, z, u, v + vstep), y(u, v + vstep) * scale(x, y, z, u, v + vstep), z(u, v + vstep))
                    )
                    sc.doc.Objects.AddSurface(triangle)
                else:
                    triangle = NurbsSurface.CreateFromCorners(
                        Point3d(x(u, v), y(u, v), z(u, v)),
                        Point3d(x(u, v + vstep), y(u, v + vstep), z(u, v + vstep)),
                        Point3d(x(u + ustep, v + vstep) * scale(x, y, z, u + ustep, v + vstep), y(u + ustep , v + vstep) * scale(x, y, z, u + ustep, v + vstep), z(u + ustep, v + vstep))
                    )
                    sc.doc.Objects.AddSurface(triangle)
                    triangle = NurbsSurface.CreateFromCorners(
                        Point3d(x(u, v), y(u, v), z(u, v)),
                        Point3d(x(u, v + vstep), y(u, v + vstep), z(u, v + vstep)),
                        Point3d(x(u - ustep, v + vstep) * scale(x, y, z, u - ustep, v + vstep), y(u - ustep, v + vstep) * scale(x, y, z, u - ustep, v + vstep), z(u - ustep, v + vstep))
                    )
                    sc.doc.Objects.AddSurface(triangle)
            else:
                if (i % 2 == 0):
                    triangle = NurbsSurface.CreateFromCorners(
                        Point3d(x(u, v) * scale(x, y, z, u, v), y(u, v) * scale(x, y, z, u, v), z(u, v)),
                        Point3d(x(u, v + vstep), y(u, v + vstep), z(u, v + vstep)),
                        Point3d(x(u + ustep, v + vstep), y(u + ustep, v + vstep), z(u + ustep, v + vstep))
                    )
                    sc.doc.Objects.AddSurface(triangle)
                    triangle = NurbsSurface.CreateFromCorners(
                        Point3d(x(u, v) * scale(x, y, z, u, v), y(u, v) * scale(x, y, z, u, v), z(u, v)),
                        Point3d(x(u, v + vstep), y(u, v + vstep), z(u, v + vstep)),
                        Point3d(x(u - ustep, v + vstep), y(u - ustep, v + vstep), z(u - ustep, v + vstep))
                    )
                    sc.doc.Objects.AddSurface(triangle)
                else:
                    triangle = NurbsSurface.CreateFromCorners(
                        Point3d(x(u + ustep, v) * scale(x, y, z, u + ustep, v), y(u + ustep, v) * scale(x, y, z, u + ustep, v), z(u + ustep, v)),
                        Point3d(x(u, v + vstep), y(u, v + vstep), z(u, v + vstep)),
                        Point3d(x(u, v), y(u, v), z(u, v))
                    )
                    sc.doc.Objects.AddSurface(triangle)
                    triangle = NurbsSurface.CreateFromCorners(
                        Point3d(x(u - ustep, v) * scale(x, y, z, u - ustep, v), y(u - ustep, v) * scale(x, y, z, u - ustep, v), z(u - ustep, v)),
                        Point3d(x(u, v + vstep), y(u, v + vstep), z(u, v + vstep)),
                        Point3d(x(u, v), y(u, v), z(u, v))
                    )
                    sc.doc.Objects.AddSurface(triangle)

offset = 1.9

# generate(x1, y1, z1, ustep, vstep)

offset = 2

generate(x2, y2, z2, ustep, vstep)

# for u in frange(0, pi * 2, ustep):
#     for v in frange(0, pi, vstep):
#         cur = Point3d(x2(u, v) * scale, y2(u, v) * scale, z2(u, v))
#         uu = u + ustep
#         vv = v
#         nex = Point3d(x2(uu, vv) * scale, y2(uu, vv) * scale, z2(uu, vv))
#         segment = Polyline((cur, nex))
#         sc.doc.Objects.AddPolyline(segment)

sc.doc.Views.Redraw()
